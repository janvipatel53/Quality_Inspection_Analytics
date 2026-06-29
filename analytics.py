# analytics helper functions for business insights

def get_risk_level(severity_score):

    if severity_score <= 20:
        return "Low"

    elif severity_score <= 50:
        return "Medium"

    elif severity_score <= 80:
        return "High"

    else:
        return "Critical"


def get_recommendation(risk_level):

    if risk_level == "Low":
        return "Minor defect. Product can be monitored."

    elif risk_level == "Medium":
        return "Moderate defect detected. Re-inspection recommended."

    elif risk_level == "High":
        return "High defect severity. Quality team review required."

    else:
        return "Critical defect detected. Reject batch immediately."


def calculate_kpis(history_data):

    total = len(history_data)

    if total == 0:
        return {
            "total_inspections": 0,
            "pass_rate": 0,
            "failure_rate": 0
        }

    passed = len(
        history_data[
            history_data["status"] == "PASS"
        ]
    )

    failed = total - passed

    pass_rate = (passed / total) * 100
    failure_rate = (failed / total) * 100

    return {
        "total_inspections": total,
        "pass_rate": round(pass_rate, 2),
        "failure_rate": round(failure_rate, 2)
    }