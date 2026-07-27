import Vision
let request = VNRecognizeTextRequest()
let supported = try! VNRecognizeTextRequest.supportedRecognitionLanguages(for: .accurate, revision: 1)
print("Supported languages:", supported.joined(separator: ", "))
