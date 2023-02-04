package com.wapwrap.api;

public class Analysis {
	private final String pdfPath;

	public Analysis(String pdfPath) {
		this.pdfPath = pdfPath;
	}

	public String getPdfPath() {
		return this.pdfPath;
	}
}
