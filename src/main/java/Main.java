import java.nio.file.Path;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("Usage: java Main <input.txt> <output.docx>");
            return;
        }

        Path inputPath = Path.of(args[0]);
        Path outputPath = Path.of(args[1]);

        NumberParser parser = new NumberParser();
        NumberFileReader reader = new NumberFileReader(parser);
        SumCalculator calculator = new SumCalculator();
        WordReportWriter writer = new WordReportWriter();

        try {
            List<Long> numbers = reader.readNumbers(inputPath);
            long sum = calculator.sum(numbers);

            writer.writeReport(
                outputPath,
                inputPath.getFileName().toString(),
                numbers.size(),
                sum
            );

            System.out.println("Done. Word file created at: " + outputPath.toAbsolutePath());
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        }
    }
}