/*
 *  Copyright (C) GridGain Systems. All Rights Reserved.
 *  _________        _____ __________________        _____
 *  __  ____/___________(_)______  /__  ____/______ ____(_)_______
 *  _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
 *  / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
 *  \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
 */

#include "ignite_runner.h"

#include "ignite/client/ignite_client_configuration.h"
#include "ignite_type.h"
#include "test_utils.h"

#include "ignite/common/detail/config.h"

#include <filesystem>
#include <sstream>
#include <stdexcept>

namespace {

/**
 * System shell command string.
 */
constexpr std::string_view SYSTEM_SHELL = IGNITE_SWITCH_WIN_OTHER("cmd.exe", "/bin/sh");
constexpr std::string_view SYSTEM_SHELL_ARG_0 = IGNITE_SWITCH_WIN_OTHER("/c ", "-c");
constexpr std::string_view GRADLEW_SCRIPT = IGNITE_SWITCH_WIN_OTHER("gradlew.bat", "./gradlew");

const std::string SERVER_ADDRESS = "127.0.0.1";

const std::string ADDITIONAL_JVM_OPTIONS_ENV = "CPP_ADDITIONAL_JVM_OPTIONS";

} // anonymous namespace

namespace ignite {

static int calc_node_port_offset(std::string_view version);

std::vector<std::string> ignite_runner::SINGLE_NODE_ADDR = {SERVER_ADDRESS + ":10942"};
std::vector<std::string> ignite_runner::NODE_ADDRS = {SERVER_ADDRESS + ":10942", SERVER_ADDRESS + ":10943"};
std::vector<std::string> ignite_runner::SSL_NODE_ADDRS = {SERVER_ADDRESS + ":10944"};
std::vector<std::string> ignite_runner::SSL_NODE_CA_ADDRS = {SERVER_ADDRESS + ":10945"};
std::vector<std::string> ignite_runner::COMPATIBILITY_NODE_ADDRS = {};

ignite_runner::ignite_runner(std::string_view version) : m_version(version) {
    COMPATIBILITY_MODE = true;
    COMPATIBILITY_NODE_ADDRS = {SERVER_ADDRESS + ":"
        + std::to_string(ignite_client_configuration::DEFAULT_PORT + calc_node_port_offset(version))};
    COMPATIBILITY_VERSION = version;
}

void ignite_runner::start() {
    std::string home = resolve_ignite_home();

    std::string work_dir;
    if (m_version) {
        work_dir = resolve_temp_dir("GridGainCompatibility", *m_version).string();
    } else {
        work_dir = home;
    }

    if (home.empty())
        throw std::runtime_error("Can not resolve Ignite home directory. Try setting IGNITE_HOME explicitly");

    std::vector<std::string> args;
    args.emplace_back(SYSTEM_SHELL_ARG_0);

    std::string command{GRADLEW_SCRIPT};

    if (m_version) {
        command += " :ignite-compatibility-tests:runnerPlatformCompatibilityTest --parallel";
    } else {
        command += " :ignite-runner:runnerPlatformTest"
                   " --no-daemon"
                   " -x compileJava"
                   " -x compileTestFixturesJava"
                   " -x compileIntegrationTestJava"
                   " -x compileTestJava";
    }

    auto additional_opts = detail::get_env(ADDITIONAL_JVM_OPTIONS_ENV);
    if (additional_opts) {
        command += " " + *additional_opts;
    }

    args.emplace_back(command);

    std::vector<std::string> env;

    if (m_version) {
        env.push_back("IGNITE_OLD_SERVER_VERSION=" + *m_version);
        env.push_back("IGNITE_OLD_SERVER_WORK_DIR=" + work_dir);

        int node_port_offset = calc_node_port_offset(*m_version);
        env.push_back("IGNITE_OLD_SERVER_PORT_OFFSET=" + std::to_string(node_port_offset));
    }

    m_process = CmdProcess::make(std::string(SYSTEM_SHELL), args, home, env);
    if (!m_process->start()) {
        m_process.reset();

        std::stringstream argsStr;
        for (auto &arg : args)
            argsStr << arg << " ";

        throw std::runtime_error("Failed to invoke Ignite command: '" + argsStr.str() + "'");
    }
}

void ignite_runner::stop() {
    if (m_process)
        m_process->kill();
}

void ignite_runner::join(std::chrono::milliseconds timeout) {
    if (m_process)
        m_process->join(timeout);
}

static int calc_node_port_offset(std::string_view version) {
    std::string port_shift;

    std::copy_if(version.begin(), version.end(), std::back_inserter(port_shift), [](auto c) { return c >= '0' && c <= '9'; });

    return stoi(port_shift);
}

} // namespace ignite