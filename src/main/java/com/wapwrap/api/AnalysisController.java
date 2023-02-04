package com.wapwrap.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.core.io.FileSystemResource;
import org.springframework.ui.ModelMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.File;
import java.io.InputStream;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import javax.servlet.http.HttpServletRequest;
import org.springframework.http.server.ServerHttpRequest;
import org.springframework.web.servlet.ModelAndView;
import javax.servlet.http.HttpServletResponse;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.UUID;


@RestController
public class AnalysisController {

	private final static Logger log = LoggerFactory.getLogger(AnalysisController.class);

	@RequestMapping("/")
	public ModelAndView index () {
		ModelAndView modelAndView = new ModelAndView();
		modelAndView.setViewName("home");
		return modelAndView;
	}
// String Home() {
// 		return "home";
// 	}

	@PostMapping("/analysis")
	public FileSystemResource analysis(
		@RequestParam final MultipartFile file,
		@RequestParam final String chatName
	) {
		// String filePath = request.getSession().getServletContext().getRealPath("/static/");
		String filePath = "/usr/local/resources/static/";
		try {
			// save the file locally
			if (!new File(filePath).exists()) {
				new File(filePath).mkdir();
			}
			log.info(String.format("upload dir: %s", filePath));
			String filename = file.getOriginalFilename();
			File dest = new File(filePath + filename);
			file.transferTo(dest);

			// write the chat name to be processed to ..static/filepath because that's where jupyter notebook will pick up the file from 
			// (difficult to pass in chat name arg to jupyter through bash)
			try (PrintWriter out = new PrintWriter(filePath + "filepath")) {
				out.println(filename);
			}

			// invoke cmd to run the jupyter notebook
			String command = String.format("/bin/sh \"%sjupyter.sh\" \"%sanalyzer.ipynb\" \"%sanalyzed/\" \"%s.pdf\"", filePath, filePath, filePath, chatName);
			log.info("Starting cmd");
			log.info(command);
			Process process = Runtime.getRuntime().exec(new String[] { "bash", "-c", command });
			BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
			String s;
			while ((s = reader.readLine()) != null) {
				log.info(s);
			}
			log.info("Finished generating pdf");

			log.info("returning the generated pdf");
			return new FileSystemResource(filePath + "analyzed/" + chatName + ".pdf");
		} catch (Exception e) {
			log.error("Error!");
			log.error(e.toString());
			return new FileSystemResource(new File(filePath));
		}
	}
}
