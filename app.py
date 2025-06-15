from flask import Flask, render_template, request
import numpy as np
import numpy_financial as npf

app = Flask(__name__)

# Function to calculate the cumilitaive interest paid
# over the term of the loan. 
def cumipmt(rate, nper, loanAmount, start_period, end_period, when=0):
    if start_period < 1 or end_period > nper:
        raise ValueError("Period range out of bounds")

    pmt = -npf.pmt(rate, nper, loanAmount)
    interest = 0

    for period in range(start_period, end_period + 1):
        if when == 1:  # payment at beginning
            interest_period = (loanAmount + pmt) * rate
        else:          # payment at end
            interest_period = loanAmount * rate
        interest += interest_period
        principal = pmt - interest_period
        loanAmount -= principal

    return round(interest, 2)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/greet', methods=['GET', 'POST'])
def greet():
    # Users variables taken from the form
    assetValue = float(request.form['assetValue'])
    downPayment = float(request.form['downPayment'])
    initialPrincipal = float(request.form['initialPrincipal'])
    apr = float(request.form['apr'])
    apy = float(request.form['apy'])
    loanTerm = int(request.form['loanTerm'])
    comp = int(request.form['comp'])
    
    ## Calculate Loan
    # Calcualted variables to be returned
    loanAmount = round(assetValue-downPayment, 2)
    nper = comp * loanTerm
    start_period = 1
    end_period = nper

    # calculate rate for the loan function
    rate = (apr/100)/12

    # Calculate cumilitave interest and total loan
    interest = cumipmt(rate, nper, loanAmount, start_period, end_period)
    loanBalance = round(loanAmount + interest, 2)


    ## Calculate Investment
    monthlyContribution = round((loanAmount-initialPrincipal)/(loanTerm*12), 2)

    i = 1
    invBalance = initialPrincipal
    while i <= nper:
        invBalance += monthlyContribution
        invBalance = round(invBalance * (1+(apy/100)/comp), 2)
        i += 1  # don't forget to increment!
    
    invReturn = round(invBalance - loanAmount, 2)


    ## Calculate overall performance
    performance = round(invReturn - interest, 2)

    # Style results
    if performance > 0:
        result_class = "positive"
    else:
        result_class = "negative"


    # Return all data back to the user on the current page. 
    return render_template('index.html', 
        loanAmount=loanAmount, 
        monthlyContribution=monthlyContribution, 
        assetValue=assetValue,
        downPayment=downPayment,
        apr=apr,
        apy=apy,
        initialPrincipal=initialPrincipal,
        loanTerm=loanTerm,
        comp=comp,
        interest=interest,
        loanBalance=loanBalance,
        invBalance=invBalance,
        invReturn=invReturn,
        performance=performance,
        result_class=result_class)    



if __name__ == '__main__':
    app.run(debug=True)
