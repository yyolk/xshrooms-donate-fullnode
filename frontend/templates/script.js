    <script type="text/javascript">
        const ws = new WebSocket("wss://xrplcluster.com");
        // const ws = new WebSocket("wss://testnet.xrpl-labs.com");
        const account = '{{ DESTINATION_WALLET }}';

        const updateProgress = m => {
                const response = JSON.parse(m.data);
                let new_balance = 0;
                if ('result' in response) {
                    console.log(response.result);
                    if ('account_data' in response.result) {
                        new_balance = Math.floor(
                            parseInt(
                                response.result.account_data.Balance
                            ) / 1e6
                        );
                    } 
                }
                if ('meta' in response) {
                    new_balance = Math.floor(
                        parseInt(
                            response
                            .meta
                            .AffectedNodes
                            .filter(node => node.ModifiedNode.FinalFields.Account == account)[0]
                            .ModifiedNode.FinalFields.Balance
                        ) / 1e6
                    );
                }
                if (new_balance) {
                    // console.log("New balance is", new_balance);
                    pbEl = document.getElementById("donationGoal")
                    pbEl.value = new_balance;
                    pbEl.classList.add('highlight');
                    setTimeout(() => pbEl.classList.remove('highlight'), 2000);
                }
        }

        ws.onopen = () => {
          ws.onmessage = m => {
            updateProgress(m);
          }
          ws.send(JSON.stringify({
            command: 'account_info', account, limit: 1
          }));
          ws.send(
              JSON.stringify({
                  command: 'subscribe',
                  accounts: [account]
              })
          );
        }
    </script>
