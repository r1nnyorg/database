import aiohttp, asyncio, argparse

parser = argparse.ArgumentParser()
parser.add_argument('clientid')
parser.add_argument('clientsecret')
parser.add_argument('tenantid')
args = parser.parse_args()
subscription='9046396e-e215-4cc5-9eb7-e25370140233'

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.post(f'https://login.microsoftonline.com/{args.tenantid}/oauth2/token', data={'grant_type':'client_credentials', 'client_id':args.clientid, 'client_secret':args.clientsecret, 'resource':'https://management.azure.com/'}) as response:
            token = (await response.json()).get('access_token')
            async with session.head(f'https://management.azure.com/subscriptions/{subscription}/resourcegroups/postgres?api-version=2021-04-01', headers={'Authorization':f'Bearer {token}'}) as response:
                if response.status == 204:
                    async with session.delete(f'https://management.azure.com/subscriptions/{subscription}/resourcegroups/postgres?api-version=2021-04-01', headers={'Authorization':f'Bearer {token}'}) as response:
                        if response.status == 202:
                            while True:
                                await asyncio.sleep(int(response.headers.get('retry-after')))
                                async with session.get(response.headers.get('location'), headers={'Authorization':f'Bearer {token}'}) as _:
                                    if _.status == 200: break
            async with session.put(f'https://management.azure.com/subscriptions/{subscription}/resourcegroups/postgres?api-version=2021-04-01', headers={'Authorization':f'Bearer {token}'}, json={'location':'westus'}) as response: pass
            async with session.put(f'https://management.azure.com/subscriptions/{subscription}/resourceGroups/postgres/providers/Microsoft.DBForPostgreSql/flexibleServers/postgrespostgres?api-version=2020-02-14-preview', headers={'Authorization':f'Bearer {token}'}, json={'location':'westus', 'sku':{'tier':'Burstable','name':'Standard_B1ms'}, 'properties':{'administratorLogin':'postgres','administratorLoginPassword':'pos1gres+','version':'13','storageProfile':{'storageMB':32768}}}) as response:
                if response.status == 202:
                    while True:
                        await asyncio.sleep(int(response.headers.get('retry-after')))
                        async with session.get(response.headers.get('azure-asyncOperation'), headers={'Authorization':f'Bearer {token}'}) as _:
                            print((await _.json()).get('status'))

asyncio.run(main())

              #token=`curl -s -d 'grant_type=client_credentials&client_id=${{secrets.CLIENTID}}&client_secret=${{secrets.CLIENTSECRET}}&resource=https%3A%2F%2Fmanagement.azure.com%2F'  | python -c "import json,sys;print(json.load(sys.stdin).get('access_token'))"`
              #curl -Is -H 'Authorization: Bearer '$token -w '%{http_code}' -o /dev/null https://management.azure.com/subscriptions/$subscription/resourcegroups/postgres?api-version=2021-04-01
              #if [ `curl -Is -H 'Authorization: Bearer '$token -w '%{http_code}' -o /dev/null https://management.azure.com/subscriptions/$subscription/resourcegroups/postgres?api-version=2021-04-01` = 204 ]
              #then
              #    curl -i -X DELETE -H 'Authorization: Bearer '$token https://management.azure.com/subscriptions/$subscription/resourcegroups/postgres?api-version=2021-04-01
              #fi
              #curl -i -X PUT -H 'Authorization: Bearer '$token -H content-type:application/json -d '{"location":"westus"}' https://management.azure.com/subscriptions/$subscription/resourcegroups/postgres?api-version=2021-04-01
              #curl -i -X PUT -H 'Authorization: Bearer '$token -H content-type:application/json -d '{"location":"westus", "sku":{"tier":"Burstable","name":"Standard_B1ms"}, "properties":{"administratorLogin":"postgres","administratorLoginPassword":"pos1gres+","version":"13","storageProfile":{"storageMB":32768}}}' https://management.azure.com/subscriptions/$subscription/resourceGroups/postgres/providers/Microsoft.DBForPostgreSql/flexibleServers/postgrespostgres?api-version=2020-02-14-preview
              #curl -i -X PUT -H 'Authorization: Bearer '$token -H content-type:application/json -d '{"properties":{"startIpAddress":"0.0.0.0","endIpAddress":"255.255.255.255"}}' https://management.azure.com/subscriptions/$subscription/resourceGroups/postgres/providers/Microsoft.DBForPostgreSql/flexibleServers/postgrespostgres/firewallRules/postgres?api-version=2020-02-14-preview
              #curl -i -X PUT -H 'Authorization: Bearer '$token -H content-type:application/json -d '{"properties":{"charset":"utf8","collation":"en_US.utf8"}}' https://management.azure.com/subscriptions/$subscription/resourceGroups/postgres/providers/Microsoft.DBForPostgreSql/flexibleServers/postgrespostgres/databases/default?api-version=2020-11-05-preview
              #az postgres flexible-server create -n postgrespostgres -g postgres -l westus -u postgres -p pos1gres+ -d default --public-access all --tier Burstable --sku-name Standard_B1ms --storage-size 32 --version 13
              #PGPASSWORD=pos1gres+ psql -h postgrespostgres.postgres.database.azure.com -U postgres -d default -f database.sql
              #if [ `curl -Is -H 'Authorization: Bearer '$token -w '%{http_code}' -o /dev/null https://management.azure.com/subscriptions/$subscription/resourcegroups/mysql?api-version=2021-04-01` = 204 ]
              #then
              #    curl -X DELETE -H 'Authorization: Bearer '$token https://management.azure.com/subscriptions/$subscription/resourcegroups/mysql?api-version=2021-04-01
              #fi
              #curl -X PUT -H 'Authorization: Bearer '$token -H content-type:application/json -d '{"location":"westus"}' https://management.azure.com/subscriptions/$subscription/resourcegroups/mysql?api-version=2021-04-01
              #az mysql flexible-server create -n mysqlmysql -g mysql -l westus -u mysql -p my1sql+my -d default --public-access all --tier Burstable --sku-name Standard_B1ms --storage-size 32 --version 8.0.21
              #mysql -h mysqlmysql.mysql.database.azure.com -u mysql -pmy1sql+my -e "SET sql_mode='ANSI_QUOTES'"
              #mysql -h mysqlmysql.mysql.database.azure.com -u mysql -pmy1sql+my -D default < database.sql
              #if `az group exists -n linux`
              #then
              #    az group delete -n linux -y
              #fi
              #az group create -n linux -l westus
              #az vm image list --offer UbuntuServer --all --output table#https://docs.microsoft.com/en-us/azure/virtual-machines/linux/tutorial-manage-vm#understand-vm-images
              #az vm list-sizes --location westus --output table#https://docs.microsoft.com/en-us/azure/virtual-machines/linux/tutorial-manage-vm#find-available-vm-sizes
              #az vm create -n linux -g linux --image Canonical:0001-com-ubuntu-server-focal:20_04-lts-gen2:latest --size Standard_B1s --admin-username chaowenguo --generate-ssh-keys --os-disk-size-gb 64
              #https://docs.microsoft.com/en-us/azure/virtual-machines/linux/nsg-quickstart#quickly-open-a-port-for-a-vm
              #az vm open-port -g linux -n linux --port 443
              #cp ~/.ssh/id_rsa `az vm show -d -g linux -n linux --query publicIps -o tsv`.key
              #ip=`ls *.key`
              #ssh -o StrictHostKeyChecking=no -i $ip chaowenguo@${ip%.key} 'sudo apt update; sudo apt purge -y snapd; wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb; sudo apt install -y --no-install-recommends docker.io ./google-chrome-stable_current_amd64.deb libx11-xcb1 x2goserver-xsession; rm google-chrome-stable_current_amd64.deb'
              #if `az group exists -n win`
              #then
              #    az group delete -n win -y
              #fi
              #az group create -n win -l westus
              #az vm create -n win -g win --image MicrosoftWindowsServer:WindowsServer:2019-datacenter-core-with-containers-smalldisk-g2:latest --size Standard_B1s --admin-username chaowenguo --admin-password HL798820y+HL798820y+ --os-disk-size-gb 64
              #az vm open-port -g win -n win --port 22
        #- uses: actions/upload-artifact@main
        #  with:
        #      path: |
        #          *.key
