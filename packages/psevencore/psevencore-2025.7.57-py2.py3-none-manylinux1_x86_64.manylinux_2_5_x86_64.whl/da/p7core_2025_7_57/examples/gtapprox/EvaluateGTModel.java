/*
 *Copyright (C) pSeven SAS, 2010-present
 *
 */
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.Files;
import java.nio.charset.Charset;
import java.io.IOException;
import java.io.BufferedReader;
import java.io.File;
import java.lang.NumberFormatException;

import net.datadvance.gtmodel.GTApproxModel;

/**
 * Sample code that loads a binary GTApprox model and evaluates model responses.
 * To compile this class use the following command:
 *
 *   javac -cp gtmodel.jar EvaluateGTModel.java
 *
 */
public class EvaluateGTModel {
  static void usage() {
    System.err.println("Usage:");
    System.err.format ("    java -cp gtmodel.jar%s. EvaluateGTModel%n", File.pathSeparator);
    System.err.println("  Print this message and exit.");
    System.err.println("");
    System.err.format ("    java -cp gtmodel.jar%s. EvaluateGTModel <model_file>%n", File.pathSeparator);
    System.err.println("  Load a GTApprox model from model_file and print model information.");
    System.err.println("");
    System.err.format ("    java -cp gtmodel.jar%s. EvaluateGTModel [-e] [-s] [-i] <model_file> <input_csv_1> ... <input_csv_N>%n", File.pathSeparator);
    System.err.println("  Load a GTApprox model from model_file and calculate model output (AE, if -e switch specified) for the inputs given in a comma-separated input file.");
    System.err.println("  Use -s switch to skip CSV header row.");
    System.err.println("  Use -i switch to print input values prior to model output.");
    System.err.println("");
    System.err.println("Model output is printed to stdout. Each line is a result for another input point.");
    System.err.println("");
    System.err.println("Print order:");
    System.err.println("  [optional input values (if -i switch is provided),]");
    System.err.println("  model (function) values,");
    System.err.println("  gradient (partial derivative) values for the first output component with respect to all input components,");
    System.err.println("  ...");
    System.err.println("  gradient (partial derivative) values for the last output component with respect to all input components.");
    System.exit(-1);
  }

  static double[] parseLine(String line, int expectedTokensNumber, Path fileName, int lineIndex) {
    if (null == line || 0 == line.length()) {
      return null;
    }

    // Disclaimer: never use this code for the real CSV parsing. It is inefficient and incomplete (does not ignore quoted commas).
    String[] stringInput = line.split(",");

    if (stringInput.length != expectedTokensNumber) {
      System.err.format("Line #%d of the file %s has invalid number of tokens: %d (%d expected)%n",
                lineIndex, fileName, stringInput.length, expectedTokensNumber);
      return null;
    }

    double[] modelInput = new double[stringInput.length];

    try {
      for (int i = 0; i < stringInput.length; i ++) {
        if (0 == stringInput[i].length()) {
          System.err.format("Line #%d of the file %s has empty field #%d. Using NaN as input value.", lineIndex, fileName, (i + 1));
          modelInput[i] = Double.NaN;
        } else {
          modelInput[i] = Double.parseDouble(stringInput[i]);
        }
      }
    } catch (NumberFormatException e) {
      System.err.format("Failed to parse line #%d of the file %s: %s%n", lineIndex, fileName, e);
      return null;
    }

    return modelInput;
  }

  public static void main(String[] args) throws IOException {
    boolean calculateAE = false;
    boolean skipHeaderRow = false;
    boolean printModelInput = false;

    // process options
    int argi = 0;
    while (argi < args.length) {
      String arg = args[argi];
      if (!arg.startsWith("-"))
        break;
      if (arg.length() < 2)
        usage();
      for (int i = 1; i < arg.length(); i ++) {
        char c = arg.charAt(i);
        switch (c) {
        case 'e':
          calculateAE = true;
          break;
        case 's':
          skipHeaderRow = true;
          break;
        case 'i':
          printModelInput = true;
          break;
        default:
          System.err.format("Invalid or unrecognized option given: %s%n%n", arg);
          usage();
        }
      }
      argi++;
    }

    // remaining arguments are the model data and CSV files to evaluate
    if (argi == args.length)
      usage();

    // load model
    Path modelPath = Paths.get(args[argi++]);
    GTApproxModel model = new GTApproxModel(Files.readAllBytes(modelPath));

    if (model == null) {
      System.err.format("Failed to load model %s%n", modelPath.toString());
      usage();
    }

    if (argi == args.length) {
      // model only is given: just print model info
      System.out.format("Model file: %s%n", modelPath.toString());
      System.out.format("Input dimension: %d%n", model.inputSize());
      System.out.format("Output dimension: %d%n", model.outputSize());
      System.out.format("Accuracy evaluation support: %s%n", (model.hasAE() ? "Yes" : "No"));
      System.out.format("Extended model information: %s%n", model.description());
    } else {
      if (calculateAE && !model.hasAE()) {
        System.err.format("AE requested but %s model does not support it.%n", modelPath.toString());
        System.exit(-2);
      }

      int modelInputSize = model.inputSize();

      // read input files
      while (argi < args.length) {
        Path dataPath = Paths.get(args[argi++]);
        Charset charset = Charset.forName("UTF-8");
        try (BufferedReader reader = Files.newBufferedReader(dataPath, charset)) {
          String line = null;
          int lineIndex = 0;

          if (skipHeaderRow) {
            reader.readLine();
            ++ lineIndex;
          }

          while ((line = reader.readLine()) != null) {
            double[] modelInput = parseLine(line.trim(), modelInputSize, dataPath, ++ lineIndex);

            if (null != modelInput) {
              if (printModelInput) {
                for (int i = 0; i < modelInput.length; i ++) {
                  System.out.format("%.17g,", modelInput[i]);
                }

              }

              double[] modelResponse;
              double[][] modelGradient;

              if (calculateAE) {
                modelResponse = model.calcAE(modelInput);
                modelGradient = model.calcGradAE(modelInput, model.GRADIENT_F_MAJOR);
              } else {
                modelResponse = model.calc(modelInput);
                modelGradient = model.calcGrad(modelInput, model.GRADIENT_F_MAJOR);
              }

              // print model response (always at least 1-dimensional)
              System.out.format("%.17g", modelResponse[0]);
              for (int i = 1; i < modelResponse.length; i ++) {
                System.out.format(",%.17g", modelResponse[i]);
              }

              // print model gradient
              for (int i = 0; i < modelGradient.length; i ++) {
                for (int j = 0; j < modelGradient[i].length; j ++) {
                  System.out.format(",%.17g", modelGradient[i][j]);
                }
              }

              System.out.format("%n");
            }
          }
        } catch (IOException e) {
          System.err.format("Failed to read file %s: %s%n", dataPath.toString(), e);
        }
      }
    }
  }
}
