import java.io.BufferedReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class NumberFileReader {
    private final NumberParser parser;

    public NumberFileReader(NumberParser parser) {
        this.parser = parser;
    }

    public List<Long> readNumbers(Path filePath) throws IOException {
        List<Long> numbers = new ArrayList<>();

        try (BufferedReader reader = Files.newBufferedReader(filePath)) {
            String line;
            int lineNumber = 0;

            while ((line = reader.readLine()) != null) {
                lineNumber++;
                String trimmed = line.trim();

                if (trimmed.isEmpty()) {
                    continue; // ignore blank lines
                }

                numbers.add(parser.parseLine(trimmed, lineNumber));
            }
        }

        return numbers;
    }
}