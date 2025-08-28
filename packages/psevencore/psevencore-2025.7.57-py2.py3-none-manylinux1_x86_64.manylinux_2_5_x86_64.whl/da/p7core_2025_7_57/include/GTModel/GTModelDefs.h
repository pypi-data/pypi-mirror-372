/*Copyright (C) pSeven SAS, 2010-present */
/**
 * @file
 *
 * General compiler definitions for GT models.
 */

#ifndef GT_MODEL_DEFS_H
#define GT_MODEL_DEFS_H

/* dynamic library export/import specifications */
#ifdef __cplusplus
  #if (defined(_WIN32) || defined(__CYGWIN__))
    /* if we are building the dynamic library (instead of using it) */
    #if defined(GT_MODEL_SHARED)
      #define GT_MODEL_API extern "C" __declspec(dllexport)
    #else
      #define GT_MODEL_API extern "C" __declspec(dllimport)
    #endif
  #else
    #if defined(GT_MODEL_SHARED)
      #define GT_MODEL_API extern "C" __attribute__((visibility("default")))
    #else
      #define GT_MODEL_API extern "C"
    #endif
  #endif
#else
  #define GT_MODEL_API
#endif

#if (defined(_WIN32) || defined(__CYGWIN__))
  #include <stddef.h>
#else
  #include <stdint.h>
#endif

#endif /* GT_MODEL_DEFS_H */
