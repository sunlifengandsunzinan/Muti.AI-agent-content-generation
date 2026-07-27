import Cocoa
import Vision

guard CommandLine.arguments.count > 1 else {
    print("Usage: ocr_korean <image_path>")
    exit(1)
}
let imagePath = CommandLine.arguments[1]

// Use NSBitmapImageRep to load image more reliably
guard let imageData = NSData(contentsOfFile: imagePath) else {
    print("Cannot read file: \(imagePath)")
    exit(1)
}
print("Loaded \(imageData.length) bytes from \(imagePath)")

guard let bitmap = NSBitmapImageRep(data: imageData as Data) else {
    print("Cannot decode image")
    exit(1)
}
print("Image: \(bitmap.pixelsWide)x\(bitmap.pixelsHigh)")

guard let cgImage = bitmap.cgImage else {
    print("Cannot get CGImage from bitmap")
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
    print("FOUND \(observations.count) text blocks")
    let texts = observations.compactMap { $0.topCandidates(1).first?.string }
    if texts.isEmpty {
        print("VISION_NO_TEXT")
    } else {
        for t in texts {
            print(t)
        }
    }
}
request.recognitionLanguages = ["ko", "en"]
request.recognitionLevel = VNRequestTextRecognitionLevel.accurate
request.usesLanguageCorrection = true

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
do {
    try handler.perform([request])
} catch {
    print("ERROR: \(error.localizedDescription)")
    exit(1)
}
