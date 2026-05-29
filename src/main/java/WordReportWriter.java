import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.apache.poi.xwpf.usermodel.XWPFRun;

import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Path;

public class WordReportWriter {

    public void writeReport(Path outputPath, String sourceFileName, int count, long sum) throws IOException {
        try (XWPFDocument document = new XWPFDocument();
             FileOutputStream out = new FileOutputStream(outputPath.toFile())) {

            XWPFParagraph title = document.createParagraph();
            XWPFRun titleRun = title.createRun();
            titleRun.setBold(true);
            titleRun.setFontSize(16);
            titleRun.setText("Number Sum Report");

            XWPFParagraph source = document.createParagraph();
            XWPFRun sourceRun = source.createRun();
            sourceRun.setText("Source file: " + sourceFileName);

            XWPFParagraph amount = document.createParagraph();
            XWPFRun amountRun = amount.createRun();
            amountRun.setText("Numbers processed: " + count);

            XWPFParagraph result = document.createParagraph();
            XWPFRun resultRun = result.createRun();
            resultRun.setBold(true);
            resultRun.setFontSize(14);
            resultRun.setText("Sum: " + sum);

            document.write(out);
        }
    }
}