import os

from flask import Flask, render_template, request

# pylint: disable=C0103
app = Flask(__name__)

global account_list
account_list = [] #account = {"id": "100", "balance": 10}

@app.route('/')
def hello():
    message = "Account Test API is running!"
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')

    return render_template('index.html',
        message=message,
        Service=service,
        Revision=revision)

@app.route('/balance', methods=['GET'])
def balance():
    account_id = request.args.get("account_id")
    for account in account_list:
        if account_id == account['id']: #found
            return str(account['balance']), 200
    #not found
    return "0", 404

@app.route('/event', methods=['POST'])
def event():
    type = request.json["type"] #required
    amount = request.json["amount"] #required

    if type == "deposit":
        destination = request.json["destination"]
        for account in account_list:
            if destination == account['id']: #found
                account['balance'] = account['balance'] + amount
                return {"destination": {"id":destination, "balance":account['balance']}}, 201
        account_list.append({"id":destination, "balance":amount}) #new account
        return {"destination": {"id":destination, "balance":amount}}, 201
    elif type == "withdraw":
        origin = request.json["origin"]
        for account in account_list:
            if origin == account['id']: #found
                account['balance'] = account['balance'] - amount #to do: verify limit
                return {"origin": {"id":origin, "balance":account['balance']}}, 201
        return "0", 404 #not found
    else: #type == transfer
        destination = request.json["destination"]
        origin = request.json["origin"]
        for account in account_list:
            if origin == account['id']: #found origin
                account['balance'] = account['balance'] - amount #to do: verify limit
                for account_dest in account_list:
                    if destination == account_dest['id']: #found destination
                        account_dest['balance'] = account_dest['balance'] + amount #plus destination balance
                        return {"origin": {"id":origin, "balance":account['balance']}, "destination": {"id":destination, "balance":account_dest['balance']}}, 201
                account_list.append({"id":destination, "balance":amount}) #new account
                return {"origin": {"id":origin, "balance":account['balance']}, "destination": {"id":destination, "balance":amount}}, 201
        return "0", 404 #not found

@app.route('/reset', methods=['POST'])
def reset():
    account_list.clear()
    return "OK", 200

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
