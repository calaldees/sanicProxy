export const hasIterationProtocol = variable => variable !== null && Symbol.iterator in Object(variable)

export function h(type, params, children) {
    const el = document.createElement(type)
    for (let [k,v] of Object.entries(params)) {el[k] = v}
    if (typeof(children)==="string") {el.appendChild(document.createTextNode(children))}
    else if (hasIterationProtocol(children)) {
        for (let c of children) {el.append(c)}
    }
    else if (children) {el.appendChild(children)}
    return el
}
