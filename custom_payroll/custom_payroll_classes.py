# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.hr.doctype.payroll_entry.payroll_entry import PayrollEntry
from frappe.utils import cint, flt
from frappe import _

def make_accrual_jv_entry(self):
    self.check_permission('write')

    journal_entry = frappe.new_doc('Journal Entry')
    journal_entry.voucher_type = 'Journal Entry'
    journal_entry.user_remark = _('Accrual Journal Entry for salaries from {0} to {1}')\
        .format(self.start_date, self.end_date)
    journal_entry.company = self.company
    journal_entry.posting_date = self.posting_date

    accounts = []
    payable_amount = 0

    jv_name = ""
    precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")
    default_payroll_payable_account = self.get_default_payroll_payable_account()
    old_branch = self.branch
    if not self.branch:
        branchs = frappe.get_all('Branch', fields = ["name", "cost_center"])
        bulk_mode = True
    else:
        branchs = [self.branch]
        bulk_mode = False
    for branch in branchs:

        if bulk_mode:
            cost_center = branch.cost_center
            self.branch = branch.name
        else:
            cost_center = self.cost_center
            self.branch = branch
        
        earnings = self.get_salary_component_total(component_type = "earnings") or {}
        deductions = self.get_salary_component_total(component_type = "deductions") or {}

        if earnings or deductions:
            

            # Earnings
            for acc, amount in earnings.items():
                payable_amount += flt(amount, precision)
                accounts.append({
                        "account": acc,
                        "debit_in_account_currency": flt(amount, precision),
                        "party_type": '',
                        "cost_center": cost_center,
                        "project": self.project,
                        "user_remark": _('Accrual Journal Entry for salaries from {0} to {1} branch: {2}').format(self.start_date, self.end_date, self.branch)
                    })

            # Deductions
            for acc, amount in deductions.items():
                payable_amount -= flt(amount, precision)
                accounts.append({
                        "account": acc,
                        "credit_in_account_currency": flt(amount, precision),
                        "cost_center": cost_center,
                        "party_type": '',
                        "project": self.project
                    })

    self.branch = old_branch
    # Payable amount
    accounts.append({
        "account": default_payroll_payable_account,
        "credit_in_account_currency": flt(payable_amount, precision),
        "party_type": '',
    })

    journal_entry.set("accounts", accounts)
    journal_entry.title = default_payroll_payable_account
    journal_entry.save()

    try:
        journal_entry.submit()
        jv_name = journal_entry.name
        self.update_salary_slip_status(jv_name = jv_name)
    except Exception as e:
        frappe.msgprint(e)

    return jv_name

def build_my_thing(doctype, event):
    PayrollEntry.make_accrual_jv_entry = make_accrual_jv_entry
