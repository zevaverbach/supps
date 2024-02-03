const getOrderElements = () => Array.from(document.querySelectorAll(".order-details-box"))

function getDateOfOrder(orderEl) {
    console.log(orderEl);
    return Date.parse(
        orderEl
        .children[0]
        .children[1]
        .innerText
        .split("Delivered on ")
        .slice(-1)[0]
    );
}

const getSupps = orderEl => Array.from(orderEl.children[1].children[0].children);

SERVINGS_LOOKUP = {
    "Liquid D-3 & MK-7": {
        numUnitsInServing: .368, 
        servingUnit: "ml",
    },
    "Crucera-SGS": {
        numUnitsInServing: 1, 
        servingUnit: "cap",
    },
    "Creatine": {
        numUnitsInServing: 5, 
        servingUnit: "g",
    },
    "Liquid Iodine Plus": {
        numUnitsInServing: .126, 
        servingUnit: "ml",
    },
};

const getNumBottles = orderEl => parseInt(orderEl
    .children[1]
    .children[0]
    .children[0]
    .children[1]
    .children[1]
    .innerText
    .split("Qty: ").slice(-1)[0]);

const SKIP_THESE = [
    "Organic Brown Mustard",
    "Sunflower Lecithin",
    "Premium Whole Flaxseed",
    "Organic Chia Seeds",
    "Raw Macadamias",
    "Hulled Hemp Seeds",
];

function makeSuppObj(sup) {
    const ord = sup.parentElement.parentElement.parentElement;
    const parts = sup.children[1].children[0].innerText.split(", ");

    // TODO: if '(' in quantityText, use that as the serving
    //       in order to get the number of servings on hand
    const quantityText = parts.slice(-1)[0];
    const servingText = parts.slice(-2, -1)[0];
    const name = parts[1];
    if (SKIP_THESE.includes(name)) {
        return null;
    }
    let numUnitsInServing, servingUnit;

    if (!servingText.includes(" ")) {
        const servingObj = SERVINGS_LOOKUP[name];
        if (servingObj == undefined) {
            throw {
                name: "servingError",
                level: "serious",
                message: `couldn't get serving info for ${name} '(${parts})'`,
                htmlMessage: this.message,
                toString: function(){return this.name + ": " + this.message;} 
            };
        } else {
            console.log(servingObj);
            ({ numUnitsInServing, servingUnit } = servingObj);
        }
    } else {
        [numUnitsInServing, servingUnit] = servingText.split(" ");
    }

    if (typeof numUnitsInServing !== "number") {
        numUnitsInServing = numUnitsInServing.replace(",", "");
    }
    numUnitsInServing = parseInt(numUnitsInServing);

    return {
        orderDate: new Date(getDateOfOrder(ord)),
        name,
        quantity: parseInt(quantityText.split(" ")[0]),
        servingUnit,
        numUnitsInServing,
        numBottles: getNumBottles(ord),
    }
}


function main(orderCutoffHuman) {
    const orderCutoff = Date.parse(orderCutoffHuman);
    const orderEls = getOrderElements().filter(el => getDateOfOrder(el) > orderCutoff)
    let suppEls = [];
    for (const orderEl of orderEls) {
        suppEls = suppEls.concat(getSupps(orderEl));
    }
    return suppEls.map(suppEl => makeSuppObj(suppEl)).filter(res => res != null);
}
