/**
 * Implements a module for displaying sample locations on a leaflet map using the GL extension.
 *
 * The WebGL approach is preferred when a large number of features are to be rendered.
 */

export class Samples {

    constructor(db) {
        this._db = db;
    }

    async init(data_source_url){
        await this._db.query("DROP TABLE IF EXISTS samples;")
        let q = `CREATE TABLE samples AS SELECT * FROM '${data_source_url}'`;
        if (data_source_url.endsWith(".jsonl")) {
            q = `CREATE TABLE samples AS SELECT * FROM read_json_auto('${data_source_url}', format='newline_delimited')`;
        }
        if (data_source_url.endsWith(".parquet")) {
            q = `CREATE TABLE samples AS SELECT * FROM read_parquet('${data_source_url}')`;
        }
        return this._db.query(q);
    }

    get totalRecords() {
        const q = 'SELECT COUNT(*) as n FROM samples;';
        return this._db.queryRow(q).then((res) => {
            return res.n
        }).catch((e) => {
            console.log(e);
            return 0;
        });
    }

    async allRows(){
        const q = 'SELECT sample_identifier as pid, label, source_collection FROM samples;';
        return this._db.query(q);
    }

    async getRecordsByBB(bb) {
        /*
        Returns x,y,pid of samples within bounding box of
          [min_x, min_y, max_x, max_y]
         */
        const q = `select 
          produced_by.sampling_site.sample_location.longitude as x,
          produced_by.sampling_site.sample_location.latitude as y,
          source_collection as source,  
          sample_identifier as pid from samples 
          where x>=${bb[0]} and x<=${bb[2]} and y>=${bb[1]} and y<=${bb[2]};`;
        return this._db.query(q);
    }

    async getRecordsById(pid) {
        /*
        Returns records that have the same location as the record with the specified identifier.
         */
        const q = `select sample_identifier, source_collection, label from samples s
            inner join (select produced_by.sampling_site.sample_location.longitude as x,
              produced_by.sampling_site.sample_location.latitude as y from samples 
              where sample_identifier='${pid}') sm
            on s.produced_by.sampling_site.sample_location.longitude=sm.x
            and produced_by.sampling_site.sample_location.latitude=sm.y;`;
        return this._db.query(q);
    }
}

