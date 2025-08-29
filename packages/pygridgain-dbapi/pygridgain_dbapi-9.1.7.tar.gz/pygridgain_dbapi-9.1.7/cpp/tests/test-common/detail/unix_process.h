/*
 *  Copyright (C) GridGain Systems. All Rights Reserved.
 *  _________        _____ __________________        _____
 *  __  ____/___________(_)______  /__  ____/______ ____(_)_______
 *  _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
 *  / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
 *  \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
 */

#pragma once

// It's OK that this code is entirely in header as it only supposed to be included from a single file.

#include "cmd_process.h"

#include <chrono>
#include <iostream>
#include <string>
#include <vector>

#ifdef __APPLE__
# include <csignal>
#endif
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

namespace ignite::detail {

/**
 * Implementation of CmdProcess for UNIX and UNIX-like systems.
 */
class UnixProcess : public ignite::CmdProcess {
public:
    /**
     * Constructor.
     *
     * @param command Command.
     * @param args Arguments.
     * @param workDir Working directory.
     * @param env Environment variables.
     */
    UnixProcess(std::string command, std::vector<std::string> args, std::string workDir, std::vector<std::string> env)
        : m_running(false)
        , m_command(std::move(command))
        , m_args(std::move(args))
        , m_workDir(std::move(workDir))
        , m_env(std::move(env)) {}

    /**
     * Destructor.
     */
    ~UnixProcess() override { kill(); }

    /**
     * Start process.
     */
    bool start() final {
        if (m_running)
            return false;

        m_pid = fork();

        if (!m_pid) {
            // Setting the group ID to be killed easily.
            int res = setpgid(0, 0);
            if (res) {
                std::cout << "Failed set group ID of the forked process: " + std::to_string(res) << std::endl;
                exit(1);
            }

            // Route for the forked process.
            res = chdir(m_workDir.c_str());
            if (res) {
                std::cout << "Failed to change directory of the forked process: " + std::to_string(res) << std::endl;
                exit(1);
            }

            std::vector<const char *> args;
            args.reserve(m_args.size() + 2);
            args.push_back(m_command.c_str());

            for (auto &arg : m_args) {
                args.push_back(arg.c_str());
            }

            args.push_back(nullptr);

            std::vector<const char *> env;
            env.reserve(m_env.size() + 1);

            for (auto &var : m_env) {
                env.push_back(var.c_str());
            }

            env.push_back(nullptr);

            res = execve(m_command.c_str(), const_cast<char *const *>(args.data()), const_cast<char * const *>(env.data()));

            // On success this code should never be reached because the process get replaced by a new one.
            std::cout << "Failed to execute process: " + std::to_string(res) << std::endl;
            exit(1);
        }

        m_running = true;
        return true;
    }

    /**
     * Kill the process.
     */
    void kill() final {
        if (!m_running)
            return;

        ::kill(-m_pid, SIGTERM);
    }

    /**
     * Join process.
     *
     * @param timeout Timeout.
     */
    void join(std::chrono::milliseconds) final {
        // Ignoring timeout in Linux...
        ::waitpid(m_pid, nullptr, 0);
    }

private:
    /** Running flag. */
    bool m_running;

    /** Process ID. */
    int m_pid{0};

    /** Command. */
    const std::string m_command;

    /** Arguments. */
    const std::vector<std::string> m_args;

    /** Working directory. */
    const std::string m_workDir;

    /** Environment variables. */
    const std::vector<std::string> m_env;
};

} // namespace ignite::detail
