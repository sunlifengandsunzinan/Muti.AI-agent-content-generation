#!/usr/bin/env python3
"""把D:\韩语\_extracted_images的图片传到Mac，用Vision框架OCR，结果存回Windows"""

import subprocess, os, sys, json, base64, tempfile, shutil

# 用Swift写一个韩语OCR程序
swift_code = r'''
import Cocoa
import Vision

// 从base64接收图片，返回OCR文字
func ocrImage(base64Data: String, index: Int) -> String? {
    guard let data = Data(base64Encoded: base64Data) else { return nil }
    guard let image = NSImage(data: data) else { return nil }
    
    guard let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else { return nil }
    
    let request = VNRecognizeTextRequest { request, error in
        if let error = error {
            print("Error: \(error.localizedDescription)")
            return
        }
    }
    
    // 韩语+英文+数字
    request.recognitionLanguages = ["ko-KR", "en-US"]
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    
    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    
    do {
        try handler.perform([request])
        guard let observations = request.results as? [VNRecognizedTextObservation] else { return nil }
        
        let texts = observations.compactMap { obs -> String? in
            return obs.topCandidates(1).first?.string
        }
        
        if texts.isEmpty {
            print("VISION_NO_TEXT")
            return ""
        }
        
        print(texts.joined(separator: "\n"))
    } catch {
        print("ERROR: \(error.localizedDescription)")
    }
}
'''

# 实际上我们用更直接的方式：写一个 swift 文件传到 Mac 上执行
swift_script = '''
import Cocoa
import Vision

guard CommandLine.arguments.count > 1 else { exit(1) }
let imagePath = CommandLine.arguments[1]
guard let image = NSImage(contentsOfFile: imagePath) else {
    print("Cannot load image: \\(imagePath)")
    exit(1)
}
guard let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("Cannot get CGImage")
    exit(1)
}

let request = VNRecognizeTextRequest { request, error in
    if let error = error {
        print("ERROR: \\(error.localizedDescription)")
        return
    }
    guard let observations = request.results as? [VNRecognizedTextObservation] else {
        print("VISION_NO_RESULTS")
        return
    }
    let texts = observations.compactMap { $0.topCandidates(1).first?.string }
    if texts.isEmpty {
        print("VISION_NO_TEXT")
    } else {
        print(texts.joined(separator: "\\n"))
    }
}
request.recognitionLanguages = ["ko-KR", "en-US"]
request.recognitionLevel = VNRequestTextRecognitionLevel.accurate
request.usesLanguageCorrection = true

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
do {
    try handler.perform([request])
} catch {
    print("ERROR: \\(error.localizedDescription)")
    exit(1)
}
'''

# 保存swift脚本到本地（Windows），然后传到Mac
swift_path = "/tmp/ocr_korean.swift"
local_swift = r"C:\Users\Administrator\.openclaw\workspace\ocr_korean.swift"

with open(local_swift, "w", encoding="utf-8") as f:
    f.write(swift_script)

print(f"Swift script saved to {local_swift}")
print("Swift script content:")
print(swift_script[:200])
