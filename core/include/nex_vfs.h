/**
 * @file nex_vfs.h
 * @brief NexOS Virtual File System (VFS) Abstraction
 */

#ifndef NEX_VFS_H
#define NEX_VFS_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define NEX_VFS_PATH_MAX 64
#define NEX_O_RDONLY     0x01
#define NEX_O_WRONLY     0x02
#define NEX_O_RDWR       0x03
#define NEX_O_CREAT      0x04
#define NEX_O_APPEND     0x08
#define NEX_O_TRUNC      0x10

typedef struct nex_vfs_ops {
    int (*open)(const char *path, int flags, int mode);
    int (*close)(int fd);
    int32_t (*read)(int fd, void *dst, size_t size);
    int32_t (*write)(int fd, const void *src, size_t size);
    int32_t (*seek)(int fd, int32_t offset, int whence);
    int (*sync)(int fd);
} nex_vfs_ops_t;

nex_err_t nex_vfs_init(void);
nex_err_t nex_vfs_mount(const char *mount_point, const nex_vfs_ops_t *ops, void *ctx);
nex_err_t nex_vfs_unmount(const char *mount_point);

int nex_open(const char *path, int flags, int mode);
int nex_close(int fd);
int32_t nex_read(int fd, void *dst, size_t size);
int32_t nex_write(int fd, const void *src, size_t size);
int32_t nex_seek(int fd, int32_t offset, int whence);

#ifdef __cplusplus
}
#endif

#endif /* NEX_VFS_H */
