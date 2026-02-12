import json
import os
from datetime import datetime

def driver_checks(statementOfAccount):
    """
    Placeholder function for basic checks (shared responsibility)

    """
    finReference = statementOfAccount.get("statementOfAccount", {}).get("finReference")
    soaSummaryReports = statementOfAccount.get("statementOfAccount", {}).get("soaSummaryReports", [])
    loan_status = statementOfAccount.get("statementOfAccount", {}).get("status")

    # print("DRIVER INPUT:", statementOfAccount)
    # print("TYPE:", type(statementOfAccount))
    # print("TOP LEVEL KEYS:", statementOfAccount.keys())

    if not finReference:
        return {
            "eligible": False,
            "reason": "Missing LAN No. in statementOfAccount"
        }
        
    if not soaSummaryReports:
        return {
            "eligible": False,
            "reason": "No soaSummaryReports found"
        }
    
    if loan_status != "Active":
        return {
            "eligible": False,
            "reason": "Loan Status is Inactive. Move to manual queue."
        }
    
    return None
    

def excess_refund_driver(statementOfAccount):
    """
    Determines if a refund case is eligible for excess refund.

    Args:
        statementOfAccount (dict): A dictionary containing refund case details.

    """
    soaSummaryReports = statementOfAccount.get("statementOfAccount", {}).get("soaSummaryReports", [])
    unadjusted_amount = 0
    bounce_overdue = 0
    penal_overdue = 0

    for summary in soaSummaryReports:
        component = summary.get("component")
        overdue_amount = summary.get("overdue",0)
        due_amount = summary.get("due",0)

        if component == "Unadjusted Amount":
            unadjusted_amount += due_amount
        if component == "Bounce Charges":
            bounce_overdue += overdue_amount
        if component == "Penal Charges":
            penal_overdue += overdue_amount

    transactionReports = statementOfAccount.get("statementOfAccount", {}).get("transactionReports", [])

    if unadjusted_amount > 0:
        #find the latest unadjusted amount transaction using eventCode, paymentType, creditAmount, transactionDate
        u_a_transactions = [
            tx for tx in transactionReports
            if tx.get("eventCode") == "PAYMENTRECIEVED" 
            and tx.get("creditAmount",0) == unadjusted_amount
            and tx.get("transactionDate") is not None
        ]
        # print("unadjusted amount:", unadjusted_amount)
        # print(type(unadjusted_amount))
        # for tx in transactionReports:
        #     print("credit amount:", tx.get("creditAmount"))
        #     print(type(tx.get("creditAmount")))
        #     break
        if not u_a_transactions:
            return {
                "eligible": False,
                "reason": "Cannot find any unadjusted amount transactions. Move to manual queue."
            }
        
        latest_u_a_transaction = max(
            u_a_transactions,
            key=lambda tx: tx.get("transactionDate")
        ) 
        u_a_date = latest_u_a_transaction.get("transactionDate")
        u_a_datetime = datetime.strptime(u_a_date, "%Y-%m-%d")
        todays_date = datetime.now()

        #inspect months 
        if not (u_a_datetime.year, u_a_datetime.month) == (todays_date.year, todays_date.month):
            return {
                "eligible": False,
                "reason": "Unadjusted amount not received in current month. Move to manual queue."
            }
        #check whether u_a is older than 30 days
        
        refund_transactions = [
            tx for tx in transactionReports
            if tx.get("eventCode") == "PAYMENTINSTEVENT" 
            and tx.get("accountHeader") == "REFUND"
            and tx.get("transactionDate") is not None  
            and u_a_datetime(tx.get("transactionDate")) >= u_a_date
        ]
        if refund_transactions:
            return {
                "eligible": False,
                "reason": "Refund found after unadjusted amount received. Move to manual queue."
            }   

        #check bounce_emis cleared or not
        bounce_transactions = [
            tx for tx in transactionReports
            if tx.get("eventCode") == "PRESRECPT" 
            and tx.get("status") != "Bounced"
            and tx.get("transactionDate") is not None  
            and u_a_datetime(tx.get("transactionDate")) >= u_a_date
        ]

        if bounce_transactions:
            return {
                "eligible": False,
                "reason": "Bounce EMI found after unadjusted amount received. Move to manual queue."
            }
        #check whether emi_candidate and their emi_amount
        emi_candidates = [
            tx for tx in transactionReports
            if tx.get("eventCode") == "DUEFORINSTALLMENT" 
            and tx.get("transactionDate") is not None  
            and u_a_datetime(tx.get("transactionDate")) >= u_a_date
        ]
        
        if emi_candidates:
            latest_emi = max(emi_candidates, key=lambda tx: tx.get("transactionDate"))
            emi_amount = latest_emi.get("debitAmount")
        else:
            return {
                "eligible": False,
                "reason": "No EMI candidate found after unadjusted amount received. Move to manual queue."
            }
        #check emi amount cleared or not
        if emi_amount:
            emi_cleared = [
                tx for tx in transactionReports
                if tx.get("eventCode") == "PRESRECPT" 
                and tx.get("status") == "Deposited"
                and tx.get("transactionDate") is not None  
                and u_a_datetime(tx.get("transactionDate")) >= u_a_date
            ]
            if emi_cleared:
                earliest_emi_cleared = max(emi_cleared, key=lambda tx: tx.get("transactionDate"))
                earliest_emi_cleared_date = earliest_emi_cleared.get("transactionDate")
                earliest_emi_cleared_datetime = datetime.strptime(earliest_emi_cleared_date, "%Y-%m-%d")
                earliest_emi_cleared_amount = earliest_emi_cleared.get("creditAmount")

                credit_amount = latest_u_a_transaction.get("creditAmount")
                if earliest_emi_cleared_datetime.year == u_a_datetime.year and earliest_emi_cleared_datetime.month == u_a_datetime.month and earliest_emi_cleared_amount != credit_amount:
                    return {
                        "eligible": False,
                        "reason": "EMI cleared date is in the same month as unadjusted amount received but amounts do not match. Move to manual queue."
                    }
                elif (earliest_emi_cleared_datetime.year != u_a_datetime.year or earliest_emi_cleared_datetime.month != u_a_datetime.month) and earliest_emi_cleared_amount == credit_amount:
                    refund_amount = credit_amount - (bounce_overdue + penal_overdue)
                    if refund_amount > 0:
                        return {
                            "eligible": True,
                            "reason": f"Eligible for excess refund of amount {refund_amount}."
                        }
                    else:
                        return {
                            "eligible": False,
                            "reason": "No excess amount after clearing EMI and overdue amounts. Move to manual queue."
                        }

            else: 
                return{
                    "eligible": False,
                    "reason": "EMI not cleared after unadjusted amount received. Move to manual queue."
                }
        else:
            return {
                "eligible": False,
                "reason": "No EMI amount found after unadjusted amount received. Move to manual queue."
            }
        

    return {
            "eligible": False,
            "reason": "No excess amount found. Move to manual queue."
        }

#Wrapper function to combine driver checks and excess refund checks
def driver(statementOfAccount: dict) -> dict:
    basic_result = driver_checks(statementOfAccount)
    if basic_result is not None:
        return basic_result

    return excess_refund_driver(statementOfAccount)