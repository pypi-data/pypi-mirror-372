/*Copyright (C) pSeven SAS, 2010-present */
/**
 * @file
 *
 * GT model interface for approximation.
 *
 * Usage example:
 *
 * // Load model from the file.
 * GTModelError* errorDescription = 0;
 * GTApproxModel* approx = GTApproxModelLoad("./my_precious_model.gta", &errorDescription);
 * if (!approx) {
 *   perror("Failed to load model!");
 *   if (errorDescription) {
 *     perror(GTModelErrorDescription(errorDescription));
 *     GTModelErrorFree(errorDescription); // this call is required if we've called GTApproxModelLoad() with non-NULL pointer to error description
 *   }
 *   exit(EXIT_FAILURE);
 * }
 * // If GTApproxModelLoad() returns non-NULL pointer then errorDescription is NULL.
 * // So we don't need to call GTModelErrorFree(errorDescription)
 *
 * // Print some model info.
 * printf("Model input size:  %h\n", GTApproxModelInputSize(approx, 0));
 * printf("Model output size: %h\n", GTApproxModelOutputSize(approx, 0));
 * printf("Model supports AE: %h\n", GTApproxModelHasAE(approx, 0));
 * printf("Model info: \n%s\n", GTApproxModelDescription(approx, 0));
 *
 * // It's good idea to check that GTApproxModelInputSize(approx, 0) and GTApproxModelOutputSize(approx, 0) return valid values.
 * if (4 != GTApproxModelInputSize(approx, 0) || 2 != GTApproxModelOutputSize(approx, 0)) {
 *   // GTApproxModelFree() should be called to avoid memory leaks.
 *   GTApproxModelFree(approx);
 *   perror("The loaded model has invalid dimensionality!");
 *   exit(EXIT_FAILURE);
 * }
 *
 * // Let's define single test point for example.
 * const double X[4] = {1., 2., 3., 4.};
 * double F[2];
 * double dFdX[2][4]; // dFdX[i][j] holds partial derivative of the i-th model output with respect to the j-th model input variable
 *
 * // Evaluate model value at point X.
 * if (GTApproxModelCalc(approx, X, 1, F, 1, &errorDescription)) {
 *   printf("F = {%g, %g}\n", F[0], F[1]);
 * } else {
 *   // Actually, the errorDescription won't be NULL in this case but let's check it by paranoid reasons.
 *   if (errorDescription) {
 *     perror(GTModelErrorDescription(errorDescription));
 *     GTModelErrorFree(errorDescription);
 *   } else {
 *     perror("Failed to evaluate model!");
 *   }
 * }
 *
 * // Evaluate model gradient at point X.
 * if (GTApproxModelGrad(approx, X, 1, dFdX, 4, 1)) {
 *   printf("dF_0/dX_j = {%g, %g, %g, %g}\n", dFdX[0][0], dFdX[0][1], dFdX[0][2], dFdX[0][3]);
 *   printf("dF_1/dX_j = {%g, %g, %g, %g}\n", dFdX[1][0], dFdX[1][1], dFdX[1][2], dFdX[1][3]);
 * } else {
 *   if (errorDescription) {
 *     perror(GTModelErrorDescription(errorDescription));
 *     GTModelErrorFree(errorDescription);
 *   } else {
 *     perror("Failed to evaluate model gradient!");
 *   }
 * }
 *
 * // The accuracy evaluation feature is optional.
 * if (GTApproxModelHasAE(approx, 0)) {
 *   double AE[2]; // AE has the same dimensionality as the model output has.
 *   double dAEdX[2][4];
 *
 *   if (GTApproxModelCalcAE(approx, X, 1, AE, 1)) {
 *     printf("AE = {%g, %g}\n", AE[0], AE[1]);
 *   } else {
 *     if (errorDescription) {
 *       perror(GTModelErrorDescription(errorDescription));
 *       GTModelErrorFree(errorDescription);
 *     } else {
 *       perror("Failed to evaluate model AE!");
 *     }
 *   }
 *
 *   if (GTApproxModelGradAE(approx, X, 1, dAEdX, 4, 1)) {
 *     printf("dF_0/dX_j = {%g, %g, %g, %g}\n", dFdX[0][0], dFdX[0][1], dFdX[0][2], dFdX[0][3]);
 *     printf("dF_1/dX_j = {%g, %g, %g, %g}\n", dFdX[1][0], dFdX[1][1], dFdX[1][2], dFdX[1][3]);
 *   } else {
 *     if (errorDescription) {
 *       perror(GTModelErrorDescription(errorDescription));
 *       GTModelErrorFree(errorDescription);
 *     } else {
 *       perror("Failed to evaluate model AE gradient!");
 *     }
 *   }
 * }
 *
 * // Free model resources at the end.
 * GTApproxModelFree(approx);
 *
 * exit(EXIT_SUCCESS);
 */

#ifndef GT_APPROX_MODEL_H
#define GT_APPROX_MODEL_H

#include "GTModelDefs.h"
#include "GTModelError.h"

typedef struct GTApproxModelData GTApproxModel;

/**
 * Loads approximation model from the file.
 *
 * @param[in] modelFileName - 0-terminated file name.
 * @param[in, out] errorDescription - optional pointer to memory to write pointer to error description object to.
 * @return pointer to approximation model instance or NULL on failure.
 * @note
 * - returned approximation model should be destroyed by calling @ref GTApproxModelFree();
 * - returned error description object should be destroyed by calling @ref GTModelErrorFree().
 * @sa @ref GTApproxModelMemoryLoad()
 */
GT_MODEL_API
GTApproxModel* GTApproxModelLoad(const char* modelFileName, GTModelError** errorDescription);

/**
 * Loads approximation model from the memory buffer.
 *
 * @param[in] modelBinaryData - pointer to the model binaty data.
 * @param[in] modelBinaryDataSize - size of the binary data.
 * @param[in, out] errorDescription - optional pointer to memory to write pointer to error description object to.
 * @return pointer to approximation model instance or NULL on failure.
 * @note
 * - returned approximation model should be destroyed by calling @ref GTApproxModelFree();
 * - returned error description object should be destroyed by calling @ref GTModelErrorFree().
 * @sa @ref GTApproxModelLoad()
 */
GT_MODEL_API
GTApproxModel* GTApproxModelMemoryLoad(const unsigned char* modelBinaryData, int modelBinaryDataSize, GTModelError** errorDescription);

/**
 * Destroy approximation model instance and free resources.
 *
 * @param[in] model - pointer to approximation model instance.
 * @return non-zero value on success or zero on failure.
 */
GT_MODEL_API
int GTApproxModelFree(const GTApproxModel* model);

/**
 * Get number of arguments - dimensionality of model input.
 *
 * @param[in] model - pointer to approximation model instance.
 * @param[in, out] errorDescription - optional pointer to memory to write pointer to error description object to.
 * @return dimensionality of model input.
 * @note
 * - returned error description object should be destroyed by calling @ref GTModelErrorFree().
 */
GT_MODEL_API
int GTApproxModelInputSize(const GTApproxModel* model, GTModelError** errorDescription);

/**
 * Get number of values - dimensionality of model output.
 *
 * @param[in] model - pointer to approximation model instance.
 * @param[in, out] errorDescription - optional pointer to memory to write pointer to error description object to.
 * @return dimensionality of model output.
 * @note
 * - returned error description object should be destroyed by calling @ref GTModelErrorFree().
 */
GT_MODEL_API
int GTApproxModelOutputSize(const GTApproxModel* model, GTModelError** errorDescription);

/**
 * Get model description in JSON format. This info contains all
 * technical information can be gathered from the model including
 * build-time error prediction.
 *
 * @param[in] model - pointer to approximation model instance.
 * @param[in, out] errorDescription - optional pointer to memory to write pointer to error description object to.
 * @return 0-terminated string with model description.
 * @note
 * - returned error description object should be destroyed by calling @ref GTModelErrorFree().
 */
GT_MODEL_API
const char* GTApproxModelDescription(const GTApproxModel* model, GTModelError** errorDescription);

/**
 * Evaluate model output in the specified point.
 *
 * @param[in] model - pointer to approximation model instance.
 * @param[in] X - pointer to the first element of input data
 * @param[in] incX - distance (in doubles) between elements of input vector,
 *                   i.e. j-th element of input vector is X[j*incX]
 * @param[out] F - pointer to the buffer where output data will be written to.
 *                 Buffer must be preallocated and be big enough to hold
 *                 all the data, taking into account value of @c incF parameter.
 * @param[in] incF - distance (in doubles) between elements of output vector,
 *                   i.e. i-th element of output vector is F[i*incF].
 * @param[in, out] errorDescription - optional pointer to memory to write pointer to error description object to.
 * @return non-zero value on success or zero on failure.
 * @note
 * - returned error description object should be destroyed by calling @ref GTModelErrorFree().
 */
GT_MODEL_API
int GTApproxModelCalc(const GTApproxModel* model, const double* X, int incX, double* F, int incF, GTModelError** errorDescription);

/**
 * Evaluate model gradient in the specified point.
 *
 * Partial derivative of the i-th model output with respect to j-th model input
 * will be written to the [incDF*i+incDX*j] element of buffer dFdX.
 *
 * Let's consider a model with n input variables and m output variables.
 * To store its gradient in an 'outputwise' order we should allocate
 * m-by-n dimensional buffer of doubles: double dFdX[m][n];
 * Then we call GTApproxModelGrad() with incDF=n or incDF=sizeof(dFdX)/sizeof(dFdX[0])
 * and incDX=1. So dF[i][j] holds dF_i/dX_j i.e. partial derivative of the i-th model
 * output with respect to j-th model input.
 *
 * To store model gradient in an 'inputwise' order we should allocate
 * n-by-m dimensional buffer of doubles: double dFdX[n][m]; and
 * call GTApproxModelGrad() with incDF=1 and incDX=m parameters.
 *
 * @param[in] model - pointer to approximation model instance.
 * @param[in] X - pointer to the first element of input data
 * @param[in] incX - distance (in doubles) between elements of input vector,
 *                   i.e. j-th element of input vector is X[j*incX]
 * @param[out] dFdX - pointer to the buffer where output data will be written to.
 *                    Buffer must be preallocated and be big enough to hold
 *                    all the data, taking into account value of @c incDF and @c incDX parameters.
 * @param[in] incDF - distance (in doubles) between partial derivatives for i-th and (i+1)-th model outputs
 *                    with respect to the same input.
 * @param[in] incDX - distance (in doubles) between partial derivatives for i-th output
 *                    with respect to j-th and (j+1)-th model input.
 * @param[in, out] errorDescription - optional pointer to memory to write pointer to error description object to.
 * @return non-zero value on success or zero on failure.
 * @note
 * - returned error description object should be destroyed by calling @ref GTModelErrorFree().
 */
GT_MODEL_API
int GTApproxModelGrad(const GTApproxModel* model, const double* X, int incX, double* dFdX, int incDF, int incDX, GTModelError** errorDescription);

/**
 * Indicates whether the model given has an 'Accuracy Evaluation' feature.
 *
 * @param[in] model - pointer to approximation model instance.
 * @param[in, out] errorDescription - optional pointer to memory to write pointer to error description object to.
 * @return non-zero value if the model has AE feature or zero otherwise.
 * @note
 * - returned error description object should be destroyed by calling @ref GTModelErrorFree().
 */
GT_MODEL_API
int GTApproxModelHasAE(const GTApproxModel* model, GTModelError** errorDescription);

/**
 * Calculate the accuracy evaluation estimate.
 *
 * @param[in] model - pointer to approximation model instance.
 * @param[in] X - pointer to the first element of input data
 * @param[in] incX - distance (in doubles) between elements of input vector,
 *                   i.e. j-th element of input vector is X[j*incX]
 * @param[out] AE - pointer to the buffer where accuracy evaluation estimate will be written to.
 *                  Buffer must be preallocated and be big enough to hold all the data,
 *                  taking into account value of @c incAE parameter.
 * @param[in] incAE - distance (in doubles) between elements of output vector,
 *                    i.e. i-th element of output vector is AE[i*incAE].
 * @param[in, out] errorDescription - optional pointer to memory to write pointer to error description object to.
 * @return non-zero value on success or zero on failure.
 * @note
 * - returned error description object should be destroyed by calling @ref GTModelErrorFree().
 */
GT_MODEL_API
int GTApproxModelCalcAE(const GTApproxModel* model, const double* X, int incX, double* AE, int incAE, GTModelError** errorDescription);

/**
 * Calculate gradient of the accuracy evaluation estimate.
 *
 * See @ref GTApproxModelGrad() for gradient storage description.
 *
 * @param[in] model - pointer to approximation model instance.
 * @param[in] X - pointer to the first element of input data.
 * @param[in] incX - distance (in doubles) between elements of input vector,
 *                   i.e. j-th element of input vector is X[j*incX]
 * @param[out] dAEdX - pointer to the buffer where output data will be written to.
 *                     Buffer must be preallocated and be big enough to hold
 *                     all the data, taking into account value of @c incDAE and @c incDX parameters.
 * @param[in] incDAE  - distance (in doubles) between partial derivatives for i-th and (i+1)-th model AE outputs
 *                     with respect to the same input.
 * @param[in] incDX - distance (in doubles) between partial derivatives for i-th AE output
 *                    with respect to j-th and (j+1)-th model input.
 * @param[in, out] errorDescription - optional pointer to memory to write pointer to error description object to.
 * @return non-zero value on success or zero on failure.
 * @note
 * - returned error description object should be destroyed by calling @ref GTModelErrorFree().
 */
GT_MODEL_API
int GTApproxModelGradAE(const GTApproxModel* model, const double* X, int incX, double* dAEdX, int incDAE, int incDX, GTModelError** errorDescription);


/*
 * 'Void return' GT model interface for approximation.
 *
 * The whole SciLab example:
 *
 * model_path = "my_model.gtapprox"; // my favorite model located in the current directory
 * libraryGTApproxModel=link("gtmodel-5.0alpha1-windows-x64-vc9-s.dll"); // gtmodel is in the current directory too
 * link(libraryGTApproxModel, ["GTApproxModelLoad_F", "GTApproxModelMemoryLoad_F", "GTApproxModelInputSize_F", "GTApproxModelOutputSize_F", "GTApproxModelFree_F", "GTApproxModelDescription_F", "GTApproxModelCalc_F", "GTApproxModelGrad_F", "GTApproxModelHasAE_F", "GTApproxModelCalcAE_F", "GTApproxModelGradAE_F"], "c");
 *
 * // load model
 * [model,failure_code,err_message,err_length]=call("GTApproxModelLoad_F", model_path,1,"c", 1024,4,"i", "out", [1,8],2,"c", [1,1],3,"i", [1,1024],5,"c", [1,1],4,"i");
 * if failure_code
 *   error(part(err_message,1:err_length));
 * end
 *
 * M=call("GTApproxModelInputSize_F", model,1,"c", 0,4,"i", "out", [1,1],2,"i", [1,1],3,"i", [1,1],4,"i");
 * N=call("GTApproxModelOutputSize_F", model,1,"c", 0,4,"i", "out", [1,1],2,"i", [1,1],3,"i", [1,1],4,"i");
 * disp(M, 'sizeX=');
 * disp(N, 'sizeF=');
 *
 * [failure_code, description_length]=call("GTApproxModelDescription_F", model,1,"c", 0,3,"i", "out", [1,1],2,"i", [1,1],3,"i");
 * [failure_code, description_length, description]=call("GTApproxModelDescription_F", model,1,"c", description_length,3,"i", "out", [1,1],2,"i", [1,1],3,"i", [1,description_length],4,"c");
 * disp(description, 'model description:');
 * X = rand([M,1]);
 * disp(X, 'X=');
 *
 * [F, failure_code, err_message, err_length] = call("GTApproxModelCalc_F", model,1,"c", X,2,"d", 1,3,"i", 1,5,"i", 1024,7,"i", "out", [N,1],4,"d", [1,1],6,"i", [1,1024],8,"c", [1,1],7,"i");
 * if failure_code
 *   error(part(err_message,1:err_length));
 * end
 * disp(F, 'F=');
 *
 * [dFdX, failure_code, err_message, err_length] = call("GTApproxModelGrad_F", model,1,"c", X,2,"d", 1,3,"i", 1,5,"i", N,6,"i", 1024,8,"i", "out", [N,M],4,"d", [1,1],7,"i", [1,1024],9,"c", [1,1],8,"i");
 * if failure_code
 *   error(part(err_message,1:err_length));
 * end
 * disp(dFdX, 'dFdX=');
 *
 * [hasAE, failure_code, err_message, err_length]=call("GTApproxModelHasAE_F", model,1,"c", 1024,4,"i", "out", [1,1],2,"i", [1,1],3,"i", [1,1024],5,"c", [1,1],4,"i");
 * if failure_code
 *   error(part(err_message,1:err_length));
 * end
 * disp(hasAE, 'hasAE=');
 *
 * [AE, failure_code, err_message, err_length] = call("GTApproxModelCalcAE_F", model,1,"c", X,2,"d", 1,3,"i", 1,5,"i", 1024,7,"i", "out", [N,1],4,"d", [1,1],6,"i", [1,1024],8,"c", [1,1],7,"i");
 * if failure_code
 *   error(part(err_message,1:err_length));
 * end
 * disp(AE, 'AE=');
 *
 * [dAEdX, failure_code, err_message, err_length] = call("GTApproxModelGradAE_F", model,1,"c", X,2,"d", 1,3,"i", 1,5,"i", N,6,"i", 1024,8,"i", "out", [N,M],4,"d", [1,1],7,"i", [1,1024],9,"c", [1,1],8,"i");
 * if failure_code
 *   error(part(err_message,1:err_length));
 * end
 * disp(dAEdX, 'dAEdX (expected nan at first column) =');
 *
 * [failure_code]=call("GTApproxModelFree_F", model,1,"c", 0,3,"i", "out", [1,1],2,"i", [1,1],3,"i");
 *
 * ulink(libraryGTApproxModel);
 *
 */

/*
 * This function was intentionally excluded from pSeven Core documentation
 *
 * @brief Load model data from the file.
 *
 * Parameters for SciLab call:
 *  #1 [in] string - path to the model binary data.
 *  #2 [out] 2*integer  - ID of the loaded model on success.
 *  #3 [out] 1*integer - function result code. 0 on succeess; -i if i-th parameter (one-based) had illegal value,
 *                       positive value if other kind of error occured.
 *  #4 [in,out] 1*integer - On input: length of the buffer to write error message to, i.e. the maximal number of characters
 *                                    (including terminating null character) that may be written to the error message buffer.
 *                                    Zero indicates 'required buffer size' request.
 *                          On output: If positive buffer size was provided on input then it's the number of characters
 *                                     written to the error message buffer excluding terminating null character.
 *                                     If zero or negative buffer size was provided on input then it's a required size of buffer
 *                                     to hold the whole error message including terminating null character.
 *  #5 [in] string - buffer to write error message on failure. If parameter #4 is 0 on input
 *                   then this buffer is not referenced and may be omitted.
 *
 * SciLab code with full error control:
 *   err_length = 1024; // put your favorite message buffer size here
 *   model_path = "<put here path to the model>";
 *   [model, failure_code, err_message, err_length]=call("GTApproxModelLoad_F", model_path,1,"c", err_length,4,"i", "out", [1,8],2,"c", [1,1],3,"i", [1,err_length],5,"c", [1,1],4,"i");
 *
 * SciLab code with minimal error control:
 *  [model, failure_code]=call("GTApproxModelLoad_F", "<put here path to model>",1,"c", 0,4,"i", "out", [1,8],2,"c", [1,1],3,"i", [1,1],4,"i");
 *
 * @param[in] modelFileName - path to model file.
 * @param[out] model - pointer to memory to write pointer to loaded model to.
 * @param[out] info - failure code: zero on success, non zero on failure.
 * @param[in,out] messageBufferSize - On input: size of the messageBuffer, on output: the number of characters written to the messageBuffer
 *                                    or required size of the messageBuffer to hold the whole error message.
 * @param[out] messageBuffer - optional pointer to error message buffer.
 */
GT_MODEL_API
void GTApproxModelLoad_F(const char* modelFileName, GTApproxModel** model, int* info, int* messageBufferSize, char* messageBuffer);

/*
 * This function was intentionally excluded from pSeven Core documentation
 *
 * @brief Release model resources. After call to this function the model ID becomes undetectably invalid.
 * So using invalid model ID in calls to GTApproxModel* functions leads to undefined behavior.
 *
 * Parameters:
 *  #1 [in] 2*integer  - model ID obtained via GTApproxModelLoad_F call.
 *  #2 [out] 1*integer - function result code. 0 on succeess; -i if i-th parameter (one-based) had illegal value,
 *                       positive value if other kind of error occured.
 *  #3 [in,out] 1*integer - On input: length of the buffer to write error message to, i.e. the maximal number of characters
 *                                    (including terminating null character) that may be written to the error message buffer.
 *                                    Zero indicates 'required buffer size' request.
 *                          On output: If positive buffer size was provided on input then it's the number of characters
 *                                     written to the error message buffer excluding terminating null character.
 *                                     If zero or negative buffer size was provided on input then it's a required size of buffer
 *                                     to hold the whole error message including terminating null character.
 *  #4 [in] string - buffer to write error message on failure. If parameter #3 is 0 on input
 *                   then this buffer is not referenced and may be omitted.
 *
 * SciLab code with 1K buffer buffer for error message:
 *   [failure_code, err_message, err_length]=call("GTApproxModelFree_F", model,1,"c", 1024,3,"i", "out", [1,1],2,"i", [1,1024],4,"c", [1,1],3,"i");
 *
 * SciLab code with minimal error control (preferred code for this function):
 *  [failure_code]=call("GTApproxModelFree_F", model,1,"c", 0,3,"i", "out", [1,1],2,"i", [1,1],3,"i");
 *
 * @param[in] model - pointer to memory with pointer to loaded model.
 * @param[out] info - failure code: zero on success, non zero on failure.
 * @param[in,out] messageBufferSize - On input: size of the messageBuffer, on output: the number of characters written to the messageBuffer
 *                                    or required size of the messageBuffer to hold the whole error message.
 * @param[out] messageBuffer - optional pointer to error message buffer.
 */
GT_MODEL_API
void GTApproxModelFree_F(GTApproxModel** model, int* info, int* messageBufferSize, char* messageBuffer);

/*
 * This function was intentionally excluded from pSeven Core documentation
 *
 * @brief Read model input vector size.
 *
 * Parameters for SciLab call:
 *  #1 [in] 2*integer  - model ID obtained via GTApproxModelLoad_F call. Let model have M-dimensional input and N-dimensional output.
 *  #2 [out] 1*integer  - M, size of the model input vector X
 *  #3 [out] 1*integer - function result code. 0 on succeess; -i if i-th parameter (one-based) had illegal value,
 *                       positive value if other kind of error occured.
 *  #4 [in,out] 1*integer - On input: length of the buffer to write error message to, i.e. the maximal number of characters
 *                                    (including terminating null character) that may be written to the error message buffer.
 *                                    Zero indicates 'required buffer size' request.
 *                          On output: If positive buffer size was provided on input then it's the number of characters
 *                                     written to the error message buffer excluding terminating null character.
 *                                     If zero or negative buffer size was provided on input then it's a required size of buffer
 *                                     to hold the whole error message including terminating null character.
 *  #5 [in] string - buffer to write error message on failure. If parameter #4 is 0 on input
 *                   then this buffer is not referenced and may be omitted.
 *
 * SciLab code with 1K buffer buffer for error message:
 *   [M, failure_code, err_message, err_length]=call("GTApproxModelInputSize_F", model,1,"c", 1024,4,"i", "out", [1,1],2,"i", [1,1],3,"i", [1,1024],5,"c", [1,1],4,"i");
 *   if failure_code
 *     error(part(err_message,1:err_length))
 *   end
 *
 * SciLab code with minimal error control:
 *   [M, failure_code]=call("GTApproxModelInputSize_F", model,1,"c", 0,4,"i", "out", [1,1],2,"i", [1,1],3,"i", [1,1],4,"i");
 *
 * @param[in] model - pointer to memory with pointer to loaded model.
 * @param[out] inputSize - pointer to memory to write model input dimensionality to.
 * @param[out] info - failure code: zero on success, non zero on failure.
 * @param[in,out] messageBufferSize - On input: size of the messageBuffer, on output: the number of characters written to the messageBuffer
 *                                    or required size of the messageBuffer to hold the whole error message.
 * @param[out] messageBuffer - optional pointer to error message buffer.
 */
GT_MODEL_API
void GTApproxModelInputSize_F(GTApproxModel** model, int* inputSize, int* info, int* messageBufferSize, char* messageBuffer);

/*
 * This function was intentionally excluded from pSeven Core documentation
 *
 * @brief Read model output vector size.
 *
 * Parameters for SciLab call:
 *  #1 [in] 2*integer  - model ID obtained via GTApproxModelLoad_F call. Let model have M-dimensional input and N-dimensional output.
 *  #2 [out] 1*integer  - N, size of the model output vector F
 *  #3 [out] 1*integer - function result code. 0 on succeess; -i if i-th parameter (one-based) had illegal value,
 *                       positive value if other kind of error occured.
 *  #4 [in,out] 1*integer - On input: length of the buffer to write error message to, i.e. the maximal number of characters
 *                                    (including terminating null character) that may be written to the error message buffer.
 *                                    Zero indicates 'required buffer size' request.
 *                          On output: If positive buffer size was provided on input then it's the number of characters
 *                                     written to the error message buffer excluding terminating null character.
 *                                     If zero or negative buffer size was provided on input then it's a required size of buffer
 *                                     to hold the whole error message including terminating null character.
 *  #5 [in] string - buffer to write error message on failure. If parameter #4 is 0 on input
 *                   then this buffer is not referenced and may be omitted.
 *
 * SciLab code with 1K buffer buffer for error message:
 *   [N, failure_code, err_message, err_length]=call("GTApproxModelOutputSize_F", model,1,"c", 1024,4,"i", "out", [1,1],2,"i", [1,1],3,"i", [1,1024],5,"c", [1,1],4,"i");
 *   if failure_code
 *     error(part(err_message,1:err_length))
 *   end
 *
 * SciLab code with minimal error control:
 *   [N, failure_code]=call("GTApproxModelOutputSize_F", model,1,"c", 0,4,"i", "out", [1,1],2,"i", [1,1],3,"i", [1,1],4,"i");
 *
 * @param[in] model - pointer to memory with pointer to loaded model.
 * @param[out] outputSize - pointer to memory to write model output dimensionality to.
 * @param[out] info - failure code: zero on success, non zero on failure.
 * @param[in,out] messageBufferSize - On input: size of the messageBuffer, on output: the number of characters written to the messageBuffer
 *                                    or required size of the messageBuffer to hold the whole error message.
 * @param[out] messageBuffer - optional pointer to error message buffer.
 */
GT_MODEL_API
void GTApproxModelOutputSize_F(GTApproxModel** model, int* outputSize, int* info, int* messageBufferSize, char* messageBuffer);

/*
 * This function was intentionally excluded from pSeven Core documentation
 *
 * @brief Read model description string.
 *
 * Parameters for SciLab call:
 *  #1 [in] 2*integer  - model ID obtained via GTApproxModelLoad_F call.
 *  #2 [out] 1*integer - function result code. 0 on succeess; -i if i-th parameter (one-based) had illegal value,
 *                       positive value if other kind of error occured.
 *  #3 [in,out] 1*integer - On input: length of the buffer to write error message to, i.e. the maximal number of characters
 *                                    (including terminating null character) that may be written to the error message buffer.
 *                                    Zero indicates 'required buffer size' request.
 *                          On output: If positive buffer size was provided on input then it's the number of characters
 *                                     written to the error message buffer excluding terminating null character.
 *                                     If zero or negative buffer size was provided on input then it's a required size of buffer
 *                                     to hold the whole error message including terminating null character.
 *  #4 [in] string - buffer to write model description on success or error message on failure.
 *
 * SciLab code to read model description:
 *   // first read required buffer size
 *   [failure_code, description_length]=call("GTApproxModelDescription_F", model,1,"c", 0,3,"i", "out", [1,1],2,"i", [1,1],3,"i");
 *   if 0 == failure_code
 *     // now read model description
 *     [failure_code, description_length, description]=call("GTApproxModelDescription_F", model,1,"c", description_length,3,"i", "out", [1,1],2,"i", [1,1],3,"i", [1,description_length],4,"c");
 *   end
 *
 * @param[in] model - pointer to memory with pointer to loaded model.
 * @param[out] info - failure code: zero on success, non zero on failure.
 * @param[in,out] messageBufferSize - On input: size of the messageBuffer, on output: the number of characters written to the messageBuffer
 *                                    or required size of the messageBuffer to hold the whole error message.
 * @param[out] messageBuffer - optional pointer to model description buffer. In case of failure this
 *                             buffer is used to write error message to.
 */
GT_MODEL_API
void GTApproxModelDescription_F(GTApproxModel** model, int* info, int* messageBufferSize, char* messageBuffer);

/*
 * This function was intentionally excluded from pSeven Core documentation
 *
 * @brief Calculates model response.
 *
 * Parameters for SciLab call:
 *  #1 [in] 2*integer  - model ID obtained via GTApproxModelLoad_F call. Let model have M-dimensional input and N-dimensional output.
 *  #2 [in] double array - pointer to the first element of M-dimensional input vector X
 *  #3 [in] 1*integer  - incX, distance between elements of the input vector X, usually it's 1
 *  #4 [out] double array - pointer to the first element of N-dimensional output vector F
 *  #5 [in] 1*integer  - incF, distance between elements of the output vector F, usually it's 1
 *  #6 [out] 1*integer - function result code. 0 on succeess; -i if i-th parameter (one-based) had illegal value,
 *                       positive value if other kind of error occured.
 *  #7 [in,out] 1*integer - On input: length of the buffer to write error message to, i.e. the maximal number of characters
 *                                    (including terminating null character) that may be written to the error message buffer.
 *                                    Zero indicates 'required buffer size' request.
 *                          On output: If positive buffer size was provided on input then it's the number of characters
 *                                     written to the error message buffer excluding terminating null character.
 *                                     If zero or negative buffer size was provided on input then it's a required size of buffer
 *                                     to hold the whole error message including terminating null character.
 *  #8 [in] string - buffer to write error message on failure. If parameter #7 is 0 on input
 *                   then this buffer is not referenced and may be omitted.
 *
 * Note on input/output buffers: in most cases incX and incF should be equal to 1.
 * But if you have K-by-M dimensional matrix X with rowwise input vectors and
 * pass X as is, without X(1,:) vector selection, then you should set incX to K.
 *
 * Let model has M dimensional input and N dimensional output. SciLab code with full error control:
 *   X = rand([M,1]); // generate random M-dimensional input, distance between elements is 1
 *   [F, failure_code, err_message, err_length] = call("GTApproxModelCalc_F", model,1,"c", X,2,"d", 1,3,"i", 1,5,"i", 1024,7,"i", "out", [N,1],4,"d", [1,1],6,"i", [1,1024],8,"c", [1,1],7,"i");
 *   if failure_code
 *     error(part(err_message,1:err_length))
 *   end
 *
 * The same code with minimal error control:
 *   [F, failure_code] = call("GTApproxModelCalc_F", model,1,"c", X,2,"d", 1,3,"i", 1,5,"i", 0,7,"i", "out", [N,1],4,"d", [1,1],6,"i", [1,1],7,"i");
 *
 * @param[in] model - pointer to memory with pointer to loaded model.
 * @param[in] X - pointer to first element of input vector X.
 * @param[in] incX - pointer to distance between adjacent elements of input vector X.
 * @param[out] F - pointer to first element of output vector F.
 * @param[in] incF - pointer to distance between adjacent elements of output vector F.
 * @param[out] info - failure code: zero on success, non zero on failure.
 * @param[in,out] messageBufferSize - On input: size of the messageBuffer, on output: the number of characters written to the messageBuffer
 *                                    or required size of the messageBuffer to hold the whole error message.
 * @param[out] messageBuffer - optional pointer to error message buffer.
 */
GT_MODEL_API
void GTApproxModelCalc_F(GTApproxModel** model, double* X, int* incX, double* F, int* incF,
                         int* info, int* messageBufferSize, char* messageBuffer);

/*
 * This function was intentionally excluded from pSeven Core documentation
 *
 * @brief Calculates models' outputwise partial derivatives with respect to model inputs.
 *
 * Parameters for SciLab call:
 *  #1 [in] 2*integer  - model ID obtained via GTApproxModelLoad_F call. Let model have M-dimensional input and N-dimensional output.
 *  #2 [in] double array - pointer to the first element of M-dimensional input vector X
 *  #3 [in] 1*integer  - incX, distance between elements of the input vector X, usually it's 1
 *  #4 [out] double array - pointer to array dFdX to write model's partial derivatives with respect to model inputs to.
 *  #5 [in] 1*integer - incDF, distance between elements dF(i)/dX(j) and dF(i+1)/dX(j) i.e. distance between array elements
 *                      to write partial derivatives for adjacent outputs with respect to the same input.
 *  #6 [in] 1*integer - incDX, distance between elements dF(i)/dX(j) and dF(i)/dX(j+1) i.e. distance between array elements
 *                      to write partial derivatives for the same output with respect to the adjacent inputs.
 *  #7 [out] 1*integer - function result code. 0 on succeess; -i if i-th parameter (one-based) had illegal value,
 *                       positive value if other kind of error occured.
 *  #8 [in,out] 1*integer - On input: length of the buffer to write error message to, i.e. the maximal number of characters
 *                                    (including terminating null character) that may be written to the error message buffer.
 *                                    Zero indicates 'required buffer size' request.
 *                          On output: If positive buffer size was provided on input then it's the number of characters
 *                                     written to the error message buffer excluding terminating null character.
 *                                     If zero or negative buffer size was provided on input then it's a required size of buffer
 *                                     to hold the whole error message including terminating null character.
 *  #9 [in] string - buffer to write error message on failure. If parameter #8 is 0 on input
 *                   then this buffer is not referenced and may be omitted.
 *
 * Note on output buffer: SciLab uses Fortran (columnwise) order of array elements. So, for model with M-dimensional input and
 * N-dimensional output and [N,M] dimensional buffer dFdX (output major), incDF should be 1 and incDX should be N.
 * For [M,N] dimensional buffer dFdX (input major), the incDF should be M and incDX should be 1.
 *
 * Note on input buffer: in most cases incX should be equal to 1. But if you have K-by-M dimensional matrix X with rowwise
 * input vectors and pass X as is, without X(1,:) vector selection, then you should set incX to K.
 *
 * Let model has M dimensional input and N dimensional output. SciLab code with 1K error message buffer:
 *   X = rand([M,1]); // generate random M-dimensional input, distance between elements is 1
 *   [dFdX, failure_code, err_message, err_length] = call("GTApproxModelGrad_F", model,1,"c", X,2,"d", 1,3,"i", 1,5,"i", N,6,"i", 1024,8,"i", "out", [N,M],4,"d", [1,1],7,"i", [1,1024],9,"c", [1,1],8,"i");
 *   if failure_code
 *     error(part(err_message,1:err_length))
 *   end
 * now dFdX is N-by-M dimensional matrix, where dFdX(i,j) is partial derivative of the i-th model output with respect to j-th model input.
 * Don't forget to check that failure_code is equal to 0.
 *
 * The same code with minimal error control:
 *   [dFdX, failure_code] = call("GTApproxModelGrad_F", model,1,"c", X,2,"d", 1,3,"i", 1,5,"i", N,6,"i", 0,8,"i", "out", [N,M],4,"d", [1,1],7,"i", [1,1],8,"i");
 *
 * @param[in] model - pointer to memory with pointer to loaded model.
 * @param[in] X - pointer to first element of input vector X.
 * @param[in] incX - pointer to distance between adjacent elements of input vector X.
 * @param[out] dFdX - pointer to first element of the output matrix dF/dX.
 * @param[in] incDF - pointer to distance between partial derivatives for adjacent outputs with respect to the same input.
 * @param[in] incDX - pointer to distance between partial derivatives for the same output with respect to adjacent inputs.
 * @param[out] info - failure code: zero on success, non zero on failure.
 * @param[in,out] messageBufferSize - On input: size of the messageBuffer, on output: the number of characters written to the messageBuffer
 *                                    or required size of the messageBuffer to hold the whole error message.
 * @param[out] messageBuffer - optional pointer to error message buffer.
 */
GT_MODEL_API
void GTApproxModelGrad_F(GTApproxModel** model, double* X, int* incX, double* dFdX, int* incDF, int* incDX,
                         int* info, int* messageBufferSize, char* messageBuffer);

/*
 * This function was intentionally excluded from pSeven Core documentation
 *
 * @brief Checks whether the model has 'accuracy evaluation' feature.
 *
 * Parameters for SciLab call:
 *  #1 [in] 2*integer  - model ID obtained via GTApproxModelLoad_F call.
 *  #2 [out] 1*integer  - non zero value if model has AE, zero otherwise.
 *  #3 [out] 1*integer - function result code. 0 on succeess; -i if i-th parameter (one-based) had illegal value,
 *                       positive value if other kind of error occured.
 *  #4 [in,out] 1*integer - On input: length of the buffer to write error message to, i.e. the maximal number of characters
 *                                    (including terminating null character) that may be written to the error message buffer.
 *                                    Zero indicates 'required buffer size' request.
 *                          On output: If positive buffer size was provided on input then it's the number of characters
 *                                     written to the error message buffer excluding terminating null character.
 *                                     If zero or negative buffer size was provided on input then it's a required size of buffer
 *                                     to hold the whole error message including terminating null character.
 *  #5 [in] string - buffer to write error message on failure. If parameter #4 is 0 on input
 *                   then this buffer is not referenced and may be omitted.
 *
 * SciLab code with 1K buffer buffer for error message:
 *   [model_has_ae, failure_code, err_message, err_length]=call("GTApproxModelHasAE_F", model,1,"c", 1024,4,"i", "out", [1,1],2,"i", [1,1],3,"i", [1,1024],5,"c", [1,1],4,"i");
 *   if failure_code
 *     error(part(err_message,1:err_length))
 *   end
 *
 * SciLab code with minimal error control:
 *   [model_has_ae, failure_code]=call("GTApproxModelHasAE_F", model,1,"c", 0,4,"i", "out", [1,1],2,"i", [1,1],3,"i", [1,1],4,"i");
 *
 * @param[in] model - pointer to memory with pointer to loaded model.
 * @param[out] hasAE - pointer to integer to write AE presence indicator to.
 * @param[out] info - failure code: zero on success, non zero on failure.
 * @param[in,out] messageBufferSize - On input: size of the messageBuffer, on output: the number of characters written to the messageBuffer
 *                                    or required size of the messageBuffer to hold the whole error message.
 * @param[out] messageBuffer - optional pointer to error message buffer.
 */
GT_MODEL_API
void GTApproxModelHasAE_F(GTApproxModel** model, int* hasAE, int* info, int* messageBufferSize, char* messageBuffer);

/*
 * This function was intentionally excluded from pSeven Core documentation
 *
 * @brief Calculates the accuracy evaluation estimate. Parameters are the same as GTApproxModelCalc_F has.
 *
 * @param[in] model - pointer to memory with pointer to loaded model.
 * @param[in] X - pointer to first element of input vector X.
 * @param[in] incX - pointer to distance between adjacent elements of input vector X.
 * @param[out] AE - pointer to first element of accuracy evaluation vector AE.
 * @param[in] incAE - pointer to distance between adjacent elements of vector AE.
 * @param[out] info - failure code: zero on success, non zero on failure.
 * @param[in,out] messageBufferSize - On input: size of the messageBuffer, on output: the number of characters written to the messageBuffer
 *                                    or required size of the messageBuffer to hold the whole error message.
 * @param[out] messageBuffer - optional pointer to error message buffer.
 */
GT_MODEL_API
void GTApproxModelCalcAE_F(GTApproxModel** model, double* X, int* incX, double* AE, int* incAE,
                           int* info, int* messageBufferSize, char* messageBuffer);

/*
 * This function was intentionally excluded from pSeven Core documentation
 *
 * @brief Calculates gradient of the accuracy evaluation estimate. Parameters are the same as GTApproxModelGrad_F has.
 *
 * @param[in] model - pointer to memory with pointer to loaded model.
 * @param[in] X - pointer to first element of input vector X.
 * @param[in] incX - pointer to distance between adjacent elements of input vector X.
 * @param[out] dAEdX - pointer to first element of the output matrix dAE/dX.
 * @param[in] incDAE - pointer to distance between AE partial derivatives for adjacent model outputs with respect to the same input.
 * @param[in] incDX - pointer to distance between AE partial derivatives for the same model output with respect to adjacent inputs.
 * @param[out] info - failure code: zero on success, non zero on failure.
 * @param[in,out] messageBufferSize - On input: size of the messageBuffer, on output: the number of characters written to the messageBuffer
 *                                    or required size of the messageBuffer to hold the whole error message.
 * @param[out] messageBuffer - optional pointer to error message buffer.
 */
GT_MODEL_API
void GTApproxModelGradAE_F(GTApproxModel** model, double* X, int* incX, double* dAEdX, int* incDAE, int* incDX,
                           int* info, int* messageBufferSize, char* messageBuffer);

#endif /* GT_APPROX_MODEL_H */
