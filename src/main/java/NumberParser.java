public class NumberParser {
    public long parseLine(String line, int lineNumber) {
        String trimmed = line.trim();

        if (trimmed.isEmpty()) {
            throw new IllegalArgumentException("Empty line at line " + lineNumber);
        }

        try {
            return Long.parseLong(trimmed);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException(
                "Invalid number at line " + lineNumber + ": '" + line + "'"
            );
        }
    }
}