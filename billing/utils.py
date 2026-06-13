import os

def delete_project_invoices(project):

    payments = project.payments.exclude(
        invoice_pdf=""
    ).exclude(
        invoice_pdf__isnull=True
    )

    for payment in payments:

        try:
            if payment.invoice_pdf and os.path.exists(
                payment.invoice_pdf.path
            ):
                os.remove(
                    payment.invoice_pdf.path
                )

        except Exception as e:
            print("PDF DELETE ERROR:", e)

        payment.invoice_pdf = None
        payment.invoice_locked = False

        payment.save(
            update_fields=[
                "invoice_pdf",
                "invoice_locked"
            ]
        )