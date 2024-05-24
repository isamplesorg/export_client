/*
Implements support for getting content from iSC
 */

import { JSONParser } from 'npm:@streamparser/json';


export class iSC {
    constructor(options = {}) {
        const {
            service = "https://central.isample.xyz/isamples_central/",
            default_query = "*:*"
        } = options;
        this.service = new URL(service);
        this.default_query = default_query;
    }

    async countRecords(q) {
        const url = new URL("thing/select", this.service);
        console.log(`Query string = ${q}`);
        url.search = new URLSearchParams({
            q: q,
            rows:0,
            wt:"json"
        });
        return fetch(url)
            .then((response) => response.json())
            .then((data) => {
                const nrecs = data.response.numFound;
                console.log(`n records = ${nrecs}`);
                return nrecs;
            })
            .catch((e) => {
                console.log(e);
            })
    }

    async pointStreamGenerator(q, handler){
        const url = new URL("thing/stream", this.service);
        console.log(`Query string = ${q}`);
        url.search = new URLSearchParams({
            q: q,
            rows:10,
            fl:"source,id,x:producedBy_samplingSite_location_longitude,y:producedBy_samplingSite_location_latitude"
        });
        fetch(url)
            .then(async (response) => {
                const jsonparser = new JSONParser({
                    stringBufferSise: undefined,
                    paths: ['$.result-set.docs.*']
                });
                jsonparser.onValue = handler;
                const reader = response.body.getReader();
                while (true) {
                    const { done, value} = await reader.read();
                    if (done) {
                        break;
                    }
                    jsonparser.write(value);
                }
            })
            .catch((e) => {
                console.log(e);
            })
    }
}