import Cocoa
import Vision

guard CommandLine.arguments.count > 1 else {
    print("Usage: ocr_korean <image_path>")
    exit(1)
}
let imagePath = CommandLine.arguments[1]
guard let image = NSImage(contentsOfFile: imagePath) else {
    print("Cannot load image: \(imagePath)")
    exit(1)
}
guard let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("Cannot get CGImage")
    exit(1)
}

let request = VNRecognizeTextRequest { request, error in
    if let error = error {
        print("ERROR: \(error.localizedDescription)")
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
        print(texts.joined(separator: "\n"))
    }
}
request.recognitionLanguages = ["ko-KR", "en-US"]
request.recognitionLevel = VNRequestTextRecognitionLevel.accurate
request.usesLanguageCorrection = true

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
do {
    try handler.perform([request])
} catch {
    print("ERROR: \(error.localizedDescription)")
    exit(1)
}
