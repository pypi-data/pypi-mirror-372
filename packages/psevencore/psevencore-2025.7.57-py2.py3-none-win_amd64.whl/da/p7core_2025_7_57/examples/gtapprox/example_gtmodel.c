/*
 *Copyright (C) pSeven SAS, 2010-present
 *
 * Example of using the C interface to GTApprox models (GTModel for C).
 *
 */

#include "GTApproxModel.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void handleError(GTModelError** error, const char* prefix, int fatalError) {
  if (*error) {
    /* report and free error */
    fprintf(stderr, "%s: %s\n", prefix, GTModelErrorDescription(*error));
    GTModelErrorFree(*error);
    if (fatalError) {
      /* exit if error marked as 'fatal' */
      exit(1);
    } else {
      /* reset error variable otherwise */
      *error = 0;
    }
  }
}

int main(int argc, char* argv[]) {
  int calculateAE = 0; /* indicates whether AE calculation is requested */
  char* modelFileName = 0; /* path to the model file */
  char* inputFileName = 0; /* path to the input CSV file or '-' to use stdin */
  FILE* inputFile = stdin; /* pointer to input file (stdin by default) */

  int inputSize = 0; /* model input vector size */
  int outputSize = 0; /* model output vector size */
  int hasAE = 0; /* indicates whether the model supports AE */

  double* input; /* input buffer */
  double* output; /* output buffer */

  int linebufSize = 256; /* actual size of the input line buffer  */
  char* linebuf = (char*)malloc(linebufSize); /* input line buffer */
  int i; /* counter */

  GTApproxModel* model = 0;
  GTModelError* error = 0;

  if (argc > 1 && !strcmp(argv[1], "-e")) {
    calculateAE = 1;
  }

  if (argc > (calculateAE+1)) {
    modelFileName = argv[1 + calculateAE];
  }

  if (argc > (calculateAE+2)) {
    inputFileName = argv[2 + calculateAE];
  }

  if (!modelFileName) {
    /* print help if no model path given */
    printf(
      "Usage:\n"
      "    %s\n"
      "  Print this message and exit.\n"
      "\n"
      "    %s model_file\n"
      "  Load a GTApprox model from model_file and print model information.\n"
      "\n"
      "    %s [-e] model_file input.csv\n"
      "  Load a GTApprox model from model_file and calculate model output (AE, if -e switch specified) for the inputs given in a comma-separated input file.\n"
      "\n"
      "    %s [-e] model -\n"
      "  Load a GTApprox model from model_file and calculate model output (AE, if -e switch specified) for the input given by stdin.\n"
      "\n"
      "Model output is printed to stdout. Each line is a result for another input point.\n"
      "Print order:\n"
      "  model (function) values,\n"
      "  gradient (partial derivative) values for the first output component with respect to all input components,\n"
      "  ...\n"
      "  gradient (partial derivative) values for the last output component with respect to all input components.\n"
      "\n",
      argv[0], argv[0], argv[0], argv[0]);
    return 0;
  }

  /* load model */
  if (!(model = GTApproxModelLoad(modelFileName, &error))) {
    fprintf(stderr, "Failed to load model %s: %s\n", modelFileName, GTModelErrorDescription(error));
    GTModelErrorFree(error);
    return 1;
  }

  /* get model parameters */
  inputSize = GTApproxModelInputSize(model, 0);
  outputSize = GTApproxModelOutputSize(model, 0);
  hasAE = GTApproxModelHasAE(model, 0);

  if (!inputFileName) {
    /* print model info and exit */
    printf("Model file: %s\n", modelFileName);
    printf("Input dimension: %d\n", inputSize);
    printf("Output dimension: %d\n", outputSize);
    printf("Accuracy evaluation support: %s\n", (hasAE ? "Yes" : "No"));
    printf("Extended model information: %s\n", GTApproxModelDescription(model, 0));
    GTApproxModelFree(model);
    return 0;
  }

  /* check AE */
  if (calculateAE && !hasAE) {
    printf("The model from %s does not support accuracy evaluation.", modelFileName);
    GTApproxModelFree(model);
    return 0;
  }

  /* open input file if exists */
  if (strcmp(inputFileName, "-") && !(inputFile = fopen(inputFileName, "r"))) {
    fprintf(stderr, "Failed to open file %s for reading: %s\n", inputFileName, strerror(errno));
    GTApproxModelFree(model);
    return 2;
  }

  /* allocate input/output buffers */
  input = (double*)malloc((inputSize + 1) * sizeof(double));
  output = (double*)malloc(outputSize * (inputSize + 1) * sizeof(double));

  while(!feof(inputFile) && !ferror(inputFile)) {
    int valuesRead, linebufFill = 0;
    char *tokens;

    /* read line from the input stream */
    while (fgets(linebuf + linebufFill, linebufSize - linebufFill, inputFile)) {
      linebufFill += strlen(linebuf + linebufFill);
      if ('\n' == linebuf[linebufFill - 1]) {
        /* EOL detected */
        break;
      } else if (!(linebuf = (char*)realloc(linebuf, (linebufSize += 256)))){
        /* can not increment buffer - out of memory */
        fprintf(stderr, "Cannot allocate line buffer of size %d: out of memory!\n", linebufSize);
        return 1;
      }
    }

    /* tokenize it and read input floats */
    valuesRead = 0;
    if (linebufFill > 0) {
      for (tokens = strtok(linebuf, ","); tokens; (tokens = strtok(0, ","))) {
        char* tailptr = tokens;
        input[(valuesRead < inputSize) ? valuesRead : inputSize] = strtod(tokens, &tailptr);
        if (tailptr > tokens) {
          ++ valuesRead;
        }
      }
    }

    if (inputSize == valuesRead) {
      if (!calculateAE) {
        GTApproxModelCalc(model, input, 1, output, 1, &error);
        handleError(&error, "Failed to calculate model value", 0);
        GTApproxModelGrad(model, input, 1, output + outputSize, inputSize, 1, &error);
        handleError(&error, "Failed to calculate model gradient", 0);
      } else {
        GTApproxModelCalcAE(model, input, 1, output, 1, &error);
        handleError(&error, "Failed to estimate model AE", 0);
        GTApproxModelGradAE(model, input, 1, output + outputSize, inputSize, 1, &error);
        handleError(&error, "Failed to estimate gradient of model AE", 0);
      }

      /* print output to stdout */
      printf("%lf", output[0]);
      for (i = 1; i < outputSize * (inputSize + 1); ++ i) {
        printf(", %lf", output[i]);
      }
      printf("\n");
    } else if (valuesRead > 0) {
      /* report input error */
      fprintf(stderr, "Invalid input: %d out of %d required float values read from line.\n", valuesRead, inputSize);
    } else if (inputFile == stdin) {
      /* break on stdin, skip empty line in file */
      break;
    }
  }

  /* release resources */

  if (inputFile != stdin) {
    fclose(inputFile);
  }

  free(input);
  free(output);
  free(linebuf);

  GTApproxModelFree(model);

  return 0;
}
