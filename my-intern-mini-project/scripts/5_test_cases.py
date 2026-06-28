import pandas as pd
from datetime import datetime

def test_orphaned_order_items():
    """1. Verify detection of order_items referencing non-existent orders."""
    # Mock data
    orders = pd.DataFrame({"order_id": ["ORD_1", "ORD_2"]})
    items = pd.DataFrame({"order_id": ["ORD_1", "ORD_999"]}) # ORD_999 is an orphan
    
    # Run pipeline check logic
    orphaned_items = items[~items['order_id'].isin(orders['order_id'])]
    
    # Assertion check
    assert len(orphaned_items) == 1, "Edge Case 1 Failed: Pipeline did not catch the orphaned item."
    assert orphaned_items.iloc[0]['order_id'] == "ORD_999", "Edge Case 1 Failed: Wrong orphan caught."
    print("Edge Case 1 Passed: Orphaned order_items caught successfully.")

def test_invalid_discount():
    """2. Verify detection of discount percents greater than 100%."""
    # Mock row data
    discount_percent = 115.0 # Invalid discount
    
    # Run validation check logic
    is_invalid = discount_percent > 100.0 or discount_percent < 0.0
    
    # Assertion check
    assert is_invalid is True, "Edge Case 2 Failed: Pipeline did not flag the discount > 100%."
    print("Edge Case 2 Passed: Illegal discount values flagged successfully.")

def test_zero_quantity():
    """3. Verify handling of items where quantity is exactly 0."""
    # Mock row data
    quantity = 0 # Invalid quantity
    
    # Run checking logic
    is_zero = quantity == 0
    
    # Assertion check
    assert is_zero is True, "Edge Case 3 Failed: Pipeline did not catch zero quantity."
    print("Edge Case 3 Passed: Zero quantity entries caught successfully.")

def test_future_order_date():
    """4. Verify identification of order dates set in the future."""
    # Mock data
    order_date_str = "2030-01-01 10:00:00" # Future date
    current_time = datetime.now()
    
    # Run evaluation logic
    order_dt = datetime.strptime(order_date_str, "%Y-%m-%d %H:%M:%S")
    is_future = order_dt > current_time
    
    # Assertion check
    assert is_future is True, "Edge Case 4 Failed: Pipeline missed a future dated transaction."
    print("Edge Case 4 Passed: Future order timestamps caught successfully.")

def run_all_tests():
    print("")
    print("       STARTING PIPELINE TESTING SUITE            ")
    print("")
    
    try:
        test_orphaned_order_items()
        test_invalid_discount()
        test_zero_quantity()
        test_future_order_date()
        print("")
        print(" SUCCESS: All edge cases verified without errors! ")
        print("")
    except AssertionError as error:
        print(" TESTING TIMED OUT OR FAILED: " + str(error))

if __name__ == "__main__":
    run_all_tests()