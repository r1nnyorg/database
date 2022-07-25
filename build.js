import fetch from 'node-fetch'

const subscription = '326ccd13-f7e0-4fbf-be40-22e42ef93ad5'

async function postgres(session, token):
    const group = `https://management.azure.com/subscriptions/${subscription}/resourcegroups/postgres?api-version=2021-04-01` 
    if (globalThis.Object.is((await fetch(group, {method:'head', headers:{authorization:`Bearer ${token}`}})).status, 204))
    {
        const response = await fetch(group, {method:'delete',  headers:{authorization:`Bearer ${token}`}})
        if (globalThis.Object.is(response.status, 202))
        {
            while (true)
            {
                await new globalThis.Promise(_ => globalThis.setTimeout(_, response.headers.get('retry-after') * 1000))
                if (globalThis.Object.is(await fetch(response.headers.get('location'), {headers:{authorization:`Bearer ${token}`}}).then(_ => _.status), 200)) break
            }
        }
    }
    await fetch(group, {method:'put', headers:{authorization:`Bearer ${token}`, 'content-type':'application/json'}, body:globalThis.JSON.stringify({location:'westus2'})})   async with session.put(f'https://management.azure.com/subscriptions/{subscription}/resourcegroups/postgres?api-version=2021-04-01', headers={'Authorization':f'Bearer {token}'}, json={'location':'westus'}) as _: pass
    host = 'postgrespostgres'
    user = 'postgres'
    password = 'pos1gres+'
    default = 'default'
    async with session.put(f'https://management.azure.com/subscriptions/{subscription}/resourceGroups/postgres/providers/Microsoft.DBForPostgreSql/flexibleServers/{host}?api-version=2020-02-14-preview', headers={'Authorization':f'Bearer {token}'}, json={'location':'westus', 'sku':{'tier':'Burstable','name':'Standard_B1ms'}, 'properties':{'administratorLogin':user,'administratorLoginPassword':password,'version':'13','storageProfile':{'storageMB':32 * 1024}}}) as response:
        if response.status == 202:
            while True:
                await asyncio.sleep(int(response.headers.get('retry-after')))
                async with session.get(response.headers.get('azure-asyncOperation'), headers={'Authorization':f'Bearer {token}'}) as _:
                    if (await _.json()).get('status') == 'Succeeded': break
    async with session.put(f'https://management.azure.com/subscriptions/{subscription}/resourceGroups/postgres/providers/Microsoft.DBForPostgreSql/flexibleServers/{host}/firewallRules/postgres?api-version=2020-02-14-preview', headers={'Authorization':f'Bearer {token}'}, json={'properties':{'startIpAddress':'0.0.0.0','endIpAddress':'255.255.255.255'}}) as firewall, session.put(f'https://management.azure.com/subscriptions/{subscription}/resourceGroups/postgres/providers/Microsoft.DBForPostgreSql/flexibleServers/{host}/databases/{default}?api-version=2020-11-05-preview', headers={'Authorization':f'Bearer {token}'}, json={'properties':{'charset':'utf8','collation':'en_US.utf8'}}) as database:
        if firewall.status == 202:
            while True:
                await asyncio.sleep(int(firewall.headers.get('retry-after')))
                async with session.get(firewall.headers.get('azure-asyncOperation'), headers={'Authorization':f'Bearer {token}'}) as _:
                    if (await _.json()).get('status') == 'Succeeded': break
        if database.status == 202:
            while True:
                await asyncio.sleep(int(database.headers.get('retry-after')))
                async with session.get(database.headers.get('azure-asyncOperation'), headers={'Authorization':f'Bearer {token}'}) as _:
                    if (await _.json()).get('status') == 'Succeeded': break
    database = await asyncpg.create_pool(host=f'{host}.postgres.database.azure.com', user=user, database=default, password=password)
    await database.execute(pathlib.Path('database.sql').read_text())
    await database.close()

const token = (await fetch('https://login.microsoftonline.com/deb7ba76-72fc-4c07-833f-1628b5e92168/oauth2/token', {method:'post', body:new globalThis.URLSearchParams({grant_type:'client_credentials', client_id:'60f0699c-a6da-4a59-be81-fd413d2c68bc', client_secret:'ljEw3qnk.HcDcd85aSBLgjdJ4uA~bqPKYz', resource:'https://management.azure.com/'})}).then(_ => _.json())).access_token
