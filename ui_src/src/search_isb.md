# Proof of concept - Query iSB using Observable Framework

This is a proof of concept document for generating a simple UI for iSB using OF.

```js
const query = view(Inputs.textarea({
    label: "Query",
    value: "*:*",
    submit: true
}));
```

The current value is ${query}.

```js
const nrows = Mutable(0);
const buffer_data = {"b":[]};
const bufferPush = (r) => {
    buffer_data.b.push(r);
    dispatchEvent(new Event("bufferchange"));
}

const buffer = Generators.observe((change) => {
   const changed = () => change(buffer_data);
   addEventListener("bufferchange", changed);
   changed();
   return () => removeEventListener("bufferchange", changed);
});

function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function sleep(duration, fn, ...args) {
    await timeout(duration);
    return fn(...args);
}

async function fakeQuery(q) {
    const qv = q;
    const row = {"query": qv, "typeof":typeof(qv)};
    bufferPush(row);
    return [row];    
}

async function dependsFakeQuery(b) {
    // Do something that takes a while
    return sleep(1000, (v) => {
        nrows.value = v.length;
        return v
    }, b.b);
    //return b.b;
}
```

Depends on input to Query:

${Inputs.table(fakeQuery(query))}


Depends on output of fakeQuery (count=${nrows}): 

${Inputs.table(dependsFakeQuery(buffer))}

