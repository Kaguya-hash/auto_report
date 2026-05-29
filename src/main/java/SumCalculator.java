import java.util.List;

public class SumCalculator {
    public long sum(List<Long> numbers) {
        long total = 0L;

        for (long number : numbers) {
            total += number;
        }

        return total;
    }
}