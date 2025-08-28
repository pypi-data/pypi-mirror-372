/*Copyright (C) pSeven SAS, 2010-present */
/**
 * @file
 *
 * Helper functions to handle GT model errors.
 */

#ifndef GT_MODEL_ERROR_H
#define GT_MODEL_ERROR_H

#include "GTModelDefs.h"

typedef struct GTModelErrorImpl GTModelError;

/**
 * Destroy error description instance and free associated resources.
 * @param[in] error - pointer to error description instance
 */
GT_MODEL_API
int GTModelErrorFree(GTModelError* error);

/**
 * Returns a pointer to zero-terminated string with error description.
 *
 * This function always returns a pointer to a valid string,
 * even if given a NULL error description pointer.
 *
 * @param[in] error - pointer to error description instance
 */
GT_MODEL_API
const char* GTModelErrorDescription(const GTModelError* error);

#endif /* GT_MODEL_ERROR_H */
