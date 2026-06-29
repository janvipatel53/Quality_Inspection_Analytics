import cv2


# Main defect detection function
def detect_defects(reference_path, test_path):

    # Load images
    reference = cv2.imread(reference_path)
    test = cv2.imread(test_path)

    if reference is None or test is None:
        return {"error": "Image not found"}

    # Convert images to grayscale
    reference_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
    test_gray = cv2.cvtColor(test, cv2.COLOR_BGR2GRAY)

    # Calculate absolute difference
    difference = cv2.absdiff(reference_gray, test_gray)

    # Binary threshold
    _, threshold = cv2.threshold(
        difference,
        30,
        255,
        cv2.THRESH_BINARY
    )

    # Find contours
    contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    defect_count = 0
    total_area = 0

    # Process each contour
    for contour in contours:

        area = cv2.contourArea(contour)

        # Ignore tiny noisy regions
        if area > 20:
            defect_count += 1
            total_area += area

            x, y, w, h = cv2.boundingRect(contour)

            cv2.rectangle(
                test,
                (x, y),
                (x + w, y + h),
                (0, 0, 255),
                2
            )

    # PASS or FAIL
    if defect_count > 0:
        status = "FAIL"
    else:
        status = "PASS"

    # Severity scoring logic
    severity_score = min(
        100,
        defect_count * 15 + int(total_area / 20)
    )

    # Return structured result
    return {
        "status": status,
        "defect_count": defect_count,
        "total_area": total_area,
        "severity_score": severity_score,
        "processed_image": test
    }