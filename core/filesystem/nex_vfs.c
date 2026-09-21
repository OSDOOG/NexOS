/**
 * @file nex_vfs.c
 * @brief NexOS Virtual File System (VFS) Dispatcher Implementation
 */

#include "nex_vfs.h"
#include "nex_memory.h"
#include "nex_log.h"
#include <string.h>

#define TAG "VFS"
#define MAX_MOUNTS 4
#define MAX_FDS    16

typedef struct {
    char mount_point[32];
    const nex_vfs_ops_t *ops;
    void *ctx;
    bool in_use;
} nex_vfs_mount_t;

typedef struct {
    int vfs_index;
    int driver_fd;
    bool in_use;
} nex_vfs_file_desc_t;

static nex_vfs_mount_t s_mounts[MAX_MOUNTS];
static nex_vfs_file_desc_t s_fds[MAX_FDS];

nex_err_t nex_vfs_init(void) {
    memset(s_mounts, 0, sizeof(s_mounts));
    memset(s_fds, 0, sizeof(s_fds));
    nex_log_info(TAG, "Virtual File System initialized");
    return NEX_OK;
}

nex_err_t nex_vfs_mount(const char *mount_point, const nex_vfs_ops_t *ops, void *ctx) {
    if (!mount_point || !ops) return NEX_ERR_INVALID_ARG;

    for (int i = 0; i < MAX_MOUNTS; i++) {
        if (!s_mounts[i].in_use) {
            strncpy(s_mounts[i].mount_point, mount_point, 31);
            s_mounts[i].ops = ops;
            s_mounts[i].ctx = ctx;
            s_mounts[i].in_use = true;
            nex_log_info(TAG, "Mounted filesystem at '%s'", mount_point);
            return NEX_OK;
        }
    }
    return NEX_ERR_NO_MEM;
}

nex_err_t nex_vfs_unmount(const char *mount_point) {
    if (!mount_point) return NEX_ERR_INVALID_ARG;
    for (int i = 0; i < MAX_MOUNTS; i++) {
        if (s_mounts[i].in_use && strcmp(s_mounts[i].mount_point, mount_point) == 0) {
            s_mounts[i].in_use = false;
            nex_log_info(TAG, "Unmounted filesystem at '%s'", mount_point);
            return NEX_OK;
        }
    }
    return NEX_ERR_NOT_FOUND;
}

int nex_open(const char *path, int flags, int mode) {
    if (!path) return -1;

    for (int i = 0; i < MAX_MOUNTS; i++) {
        if (s_mounts[i].in_use) {
            size_t mlen = strlen(s_mounts[i].mount_point);
            if (strncmp(path, s_mounts[i].mount_point, mlen) == 0) {
                const char *subpath = path + mlen;
                if (*subpath == '/') subpath++;

                if (s_mounts[i].ops && s_mounts[i].ops->open) {
                    int dfd = s_mounts[i].ops->open(subpath, flags, mode);
                    if (dfd >= 0) {
                        for (int f = 0; f < MAX_FDS; f++) {
                            if (!s_fds[f].in_use) {
                                s_fds[f].vfs_index = i;
                                s_fds[f].driver_fd = dfd;
                                s_fds[f].in_use = true;
                                return f;
                            }
                        }
                        s_mounts[i].ops->close(dfd);
                        return -1;
                    }
                }
            }
        }
    }
    return -1;
}

int nex_close(int fd) {
    if (fd < 0 || fd >= MAX_FDS || !s_fds[fd].in_use) return -1;
    int v_idx = s_fds[fd].vfs_index;
    int dfd = s_fds[fd].driver_fd;
    s_fds[fd].in_use = false;

    if (s_mounts[v_idx].ops && s_mounts[v_idx].ops->close) {
        return s_mounts[v_idx].ops->close(dfd);
    }
    return 0;
}

int32_t nex_read(int fd, void *dst, size_t size) {
    if (fd < 0 || fd >= MAX_FDS || !s_fds[fd].in_use) return -1;
    int v_idx = s_fds[fd].vfs_index;
    int dfd = s_fds[fd].driver_fd;
    if (s_mounts[v_idx].ops && s_mounts[v_idx].ops->read) {
        return s_mounts[v_idx].ops->read(dfd, dst, size);
    }
    return -1;
}

int32_t nex_write(int fd, const void *src, size_t size) {
    if (fd < 0 || fd >= MAX_FDS || !s_fds[fd].in_use) return -1;
    int v_idx = s_fds[fd].vfs_index;
    int dfd = s_fds[fd].driver_fd;
    if (s_mounts[v_idx].ops && s_mounts[v_idx].ops->write) {
        return s_mounts[v_idx].ops->write(dfd, src, size);
    }
    return -1;
}

int32_t nex_seek(int fd, int32_t offset, int whence) {
    if (fd < 0 || fd >= MAX_FDS || !s_fds[fd].in_use) return -1;
    int v_idx = s_fds[fd].vfs_index;
    int dfd = s_fds[fd].driver_fd;
    if (s_mounts[v_idx].ops && s_mounts[v_idx].ops->seek) {
        return s_mounts[v_idx].ops->seek(dfd, offset, whence);
    }
    return -1;
}
