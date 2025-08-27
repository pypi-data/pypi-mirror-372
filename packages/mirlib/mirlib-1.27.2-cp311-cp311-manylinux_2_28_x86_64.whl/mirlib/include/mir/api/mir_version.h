#pragma once

#define mir_VERSION_STR "1.27.2"
#define mir_VERSION     "1.27.2"

#define mir_VERSION_MAJOR 1
#define mir_VERSION_MINOR 27
#define mir_VERSION_PATCH 2

const char * mir_version();

unsigned int mir_version_int();

const char * mir_version_str();

const char * mir_git_sha1();
