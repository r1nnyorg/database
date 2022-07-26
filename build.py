import aiohttp, asyncio, argparse, asyncpg, pathlib, asyncmy, ssl, oci, cx_Oracle, io, zipfile, re

configure = {'user':'ocid1.user.oc1..aaaaaaaalwudh6ys7562qtyfhxl4oji25zn6aapndqfuy2jfroyyielpu3pa', 'key_file':'oci.key', 'fingerprint':'bd:01:98:0d:5d:4a:6f:b2:49:b4:7f:df:43:00:32:39', 'tenancy':'ocid1.tenancy.oc1..aaaaaaaa4h5yoefhbxm4ybqy6gxl6y5cgxmdijira7ywuge3q4cbdaqnyawq', 'region':'us-sanjose-1'}
databaseClient = oci.database.DatabaseClient(configure)
databaseClientCompositeOperations = oci.database.DatabaseClientCompositeOperations(databaseClient)
password = 'ora1cle+ORAC'
dataWarehouse = oci.database.models.CreateAutonomousDatabaseBase(compartment_id=configure.get('tenancy'), db_name='dataWarehouse', admin_password=password, cpu_core_count=1, data_storage_size_in_tbs=1, db_workload='DW', is_free_tier=True)
transaction = oci.database.models.CreateAutonomousDatabaseBase(compartment_id=configure.get('tenancy'), db_name='transaction', admin_password=password, cpu_core_count=1, data_storage_size_in_tbs=1, db_workload='OLTP', is_free_tier=True)
#databaseClientCompositeOperations.create_autonomous_database_and_wait_for_state(dataWarehouse, wait_for_states=[oci.database.models.AutonomousDatabase.LIFECYCLE_STATE_AVAILABLE])
#databaseClientCompositeOperations.create_autonomous_database_and_wait_for_state(transaction, wait_for_states=[oci.database.models.AutonomousDatabase.LIFECYCLE_STATE_AVAILABLE])
generateAutonomousDatabaseWalletDetails = oci.database.models.GenerateAutonomousDatabaseWalletDetails(password=password)
for _ in databaseClient.list_autonomous_databases(compartment_id=configure.get('tenancy')).data:
    zipfile.ZipFile(io.BytesIO(databaseClient.generate_autonomous_database_wallet(_.id, generateAutonomousDatabaseWalletDetails).data.content)).extractall(_.id)
    tnsnames = pathlib.Path(_.id).joinpath('tnsnames.ora').read_text()
    connection = cx_Oracle.connect('admin', password, f"tcps://{re.search('(?<=host=)[.0-9a-z-]+', tnsnames).group(0)}:1522/{re.search('(?<=service_name=)[.0-9a-z_]+', tnsnames).group(0)}?wallet_location={_.id}")
    cursor = connection.cursor()
    cursor.execute(pathlib.Path('database.sql').read_text())
#https://www.oracle.com/database/technologies/instant-client.html

parser = argparse.ArgumentParser()
for _ in ('clientid', 'clientsecret', 'tenantid'): parser.add_argument(_)
args = parser.parse_args()
subscription='9046396e-e215-4cc5-9eb7-e25370140233'

#az ad sp create-for-rbac --role Contributor --scopes /subscriptions/subscriptionID
#az login --service-principal -u appId -p password -t tenant
#az group delete -n postgres -y
#az group create -n postgres -l westus
#az postgres flexible-server create -n postgrespostgres -g postgres -l westus -u postgres -p pos1gres+ -d default --public-access all --tier Burstable --sku-name Standard_B1ms --storage-size 32 --version 13
#PGPASSWORD=pos1gres+ psql -h postgrespostgres.postgres.database.azure.com -U postgres -d default -f database.sql
async def postgres(session, token):
    async with session.head(f'https://management.azure.com/subscriptions/{subscription}/resourcegroups/postgres?api-version=2021-04-01', headers={'Authorization':f'Bearer {token}'}) as response:
        if response.status == 204:
            async with session.delete(f'https://management.azure.com/subscriptions/{subscription}/resourcegroups/postgres?api-version=2021-04-01', headers={'Authorization':f'Bearer {token}'}) as response:
                if response.status == 202:
                    while True:
                        await asyncio.sleep(int(response.headers.get('retry-after')))
                        async with session.get(response.headers.get('location'), headers={'Authorization':f'Bearer {token}'}) as _:
                            if _.status == 200: break
    async with session.put(f'https://management.azure.com/subscriptions/{subscription}/resourcegroups/postgres?api-version=2021-04-01', headers={'Authorization':f'Bearer {token}'}, json={'location':'westus'}) as _: pass
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

#az group delete -n mysql -y
#az group create -n mysql -l westus
#az mysql flexible-server create -n mysqlmysql -g mysql -l westus -u mysql -p my1sql+my -d default --public-access all --tier Burstable --sku-name Standard_B1ms --storage-size 32 --version 8.0.21
#mysql -h mysqlmysql.mysql.database.azure.com -u mysql -pmy1sql+my -D default < database.sql
async def mysql(session, token):
    async with session.head(f'https://management.azure.com/subscriptions/{subscription}/resourcegroups/mysql?api-version=2021-04-01', headers={'Authorization':f'Bearer {token}'}) as response:
        if response.status == 204:
            async with session.delete(f'https://management.azure.com/subscriptions/{subscription}/resourcegroups/mysql?api-version=2021-04-01', headers={'Authorization':f'Bearer {token}'}) as response:
                if response.status == 202:
                    while True:
                        await asyncio.sleep(int(response.headers.get('retry-after')))
                        async with session.get(response.headers.get('location'), headers={'Authorization':f'Bearer {token}'}) as _:
                            if _.status == 200: break
    async with session.put(f'https://management.azure.com/subscriptions/{subscription}/resourcegroups/mysql?api-version=2021-04-01', headers={'Authorization':f'Bearer {token}'}, json={'location':'westus'}) as _: pass
    host = 'mysqlmysql'
    user = 'mysql'
    password = 'my1sql+my'
    default = 'defaultt'
    async with session.put(f'https://management.azure.com/subscriptions/{subscription}/resourceGroups/mysql/providers/Microsoft.DBForMySql/flexibleServers/{host}?api-version=2020-07-01-preview', headers={'Authorization':f'Bearer {token}'}, json={'location':'westus', 'sku':{'tier':'Burstable','name':'Standard_B1ms'}, 'properties':{'administratorLogin':user,'administratorLoginPassword':password,'version':'8.0.21','storageProfile':{'storageMB':32 * 1024}}}) as response:
        if response.status == 202:
            while True:
                await asyncio.sleep(int(response.headers.get('retry-after')))
                async with session.get(response.headers.get('azure-asyncOperation'), headers={'Authorization':f'Bearer {token}'}) as _:
                    if (await _.json()).get('status') == 'Succeeded': break
    async with session.put(f'https://management.azure.com/subscriptions/{subscription}/resourceGroups/mysql/providers/Microsoft.DBForMySql/flexibleServers/{host}/firewallRules/mysql?api-version=2020-07-01-preview', headers={'Authorization':f'Bearer {token}'}, json={'properties':{'startIpAddress':'0.0.0.0','endIpAddress':'255.255.255.255'}}) as firewall, session.put(f'https://management.azure.com/subscriptions/{subscription}/resourceGroups/mysql/providers/Microsoft.DBForMySql/flexibleServers/{host}/databases/{default}?api-version=2020-07-01-preview', headers={'Authorization':f'Bearer {token}'}, json={'properties':{'charset':'utf8','collation':'utf8_general_ci'}}) as database:
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
    database = await asyncmy.create_pool(host=f'{host}.mysql.database.azure.com', user=user, db=default, password=password, sql_mode='ANSI_QUOTES', ssl=ssl.create_default_context(cafile='DigiCertGlobalRootCA.crt.pem'))
    async with database.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(pathlib.Path('database.sql').read_text())
    database.close()
    await database.wait_closed()
    
async def main():
    async with aiohttp.ClientSession() as session:
        async with session.post(f'https://login.microsoftonline.com/{args.tenantid}/oauth2/token', data={'grant_type':'client_credentials', 'client_id':args.clientid, 'client_secret':args.clientsecret, 'resource':'https://management.azure.com/'}) as response:
            token = (await response.json()).get('access_token')
            await asyncio.gather(postgres(session, token), mysql(session, token))
            
#asyncio.run(main())
