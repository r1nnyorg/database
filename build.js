import fetch from 'node-fetch'

const token = (await fetch('https://login.microsoftonline.com/deb7ba76-72fc-4c07-833f-1628b5e92168/oauth2/token', {method:'post', body:new globalThis.URLSearchParams({grant_type:'client_credentials', client_id:'60f0699c-a6da-4a59-be81-fd413d2c68bc', client_secret:'ljEw3qnk.HcDcd85aSBLgjdJ4uA~bqPKYz', resource:'https://management.azure.com/'})}).then(_ => _.json())).access_token
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
await fetch(group, {method:'put', headers:{authorization:`Bearer ${token}`, 'content-type':'application/json'}, body:globalThis.JSON.stringify({location:'westus2'})})
