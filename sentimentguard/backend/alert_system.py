"""
Triggers alerts if risk exceeds threshold. Logs warnings.
"""
import logging

def trigger_alert(score, threshold=70):
    """Trigger alert if score > threshold. Log warning."""
    if score > threshold:
        logging.warning(f"ALERT: Risk score {score} exceeds threshold {threshold}!")
        print(f"ALERT: Risk score {score} exceeds threshold {threshold}!")
        return True
    return False

if __name__ == "__main__":
    trigger_alert(80)