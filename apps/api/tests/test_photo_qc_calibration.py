from app.services import photo_prep


def test_no_person_image_is_rejected_before_lora_or_body_checks() -> None:
    report = photo_prep._qc_report_from_signals(
        face_detected=False,
        body_detected=False,
        blur_score=180,
        exposure_score=105,
        framing_label="unknown",
        resolution_ok=True,
    )

    assert report.bucket == "rejected"
    assert report.reason_codes == ["no_person_detected"]
    assert report.metrics["person_detected"] is False


def test_clear_face_portrait_with_weak_body_routes_to_lora_only() -> None:
    report = photo_prep._qc_report_from_signals(
        face_detected=True,
        body_detected=False,
        blur_score=180,
        exposure_score=105,
        framing_label="head-closeup",
        resolution_ok=True,
    )

    assert report.bucket == "lora_only"
    assert report.usable_for_lora is True
    assert report.usable_for_body is False
    assert "body_evidence_missing" in report.reason_codes
    assert report.metrics["face_detected"] is True
    assert report.metrics["body_detected"] is False


def test_body_shot_with_no_face_routes_to_body_only() -> None:
    report = photo_prep._qc_report_from_signals(
        face_detected=False,
        body_detected=True,
        blur_score=145,
        exposure_score=105,
        framing_label="full-body",
        resolution_ok=True,
    )

    assert report.bucket == "body_only"
    assert report.usable_for_lora is False
    assert report.usable_for_body is True
    assert report.reason_codes == ["face_required_for_lora"]
    assert report.metrics["person_detected"] is True


def test_full_usable_shot_routes_to_both_without_false_blur_reasons() -> None:
    report = photo_prep._qc_report_from_signals(
        face_detected=True,
        body_detected=True,
        blur_score=180,
        exposure_score=105,
        framing_label="full-body",
        resolution_ok=True,
    )

    assert report.bucket == "both"
    assert report.reason_codes == []
    assert report.metrics["blur_ok_for_lora"] is True
    assert report.metrics["blur_ok_for_body"] is True


def test_borderline_body_image_with_no_face_stays_body_only_not_rejected() -> None:
    report = photo_prep._qc_report_from_signals(
        face_detected=False,
        body_detected=True,
        blur_score=60,
        exposure_score=105,
        framing_label="full-body",
        resolution_ok=True,
    )

    assert report.bucket == "body_only"
    assert report.usable_for_body is True
    assert report.usable_for_lora is False
    assert "face_required_for_lora" in report.reason_codes
    assert "body_blur_borderline" in report.reason_codes
    assert report.metrics["blur_ok_for_body"] is True
    assert report.metrics["blur_ok_for_lora"] is False
