let getOrderElements = () => Array.from(document.querySelectorAll(".order-details-box"))

function getDateOfOrder(orderEl) {
    return Date.parse(
        orderEl
        .children[0]
        .children[1]
        .innerText
        .split("Delivered on ")
        .slice(-1)[0]
    );
}

let getSupps = orderEl => Array.from(orderEl.children[1].children[0].children);

SERVINGS_LOOKUP = {
    "Liquid D-3 & MK-7": {
        numUnitsInServing: .368, 
        servingUnit: "ml",
    },
    "Crucera-SGS": {
        numUnitsInServing: 1, 
        servingUnit: "caps",
    },
    "Creatine": {
        numUnitsInServing: 5, 
        servingUnit: "g",
    },
    "Liquid Iodine Plus": {
        numUnitsInServing: .126, 
        servingUnit: "ml",
    },
    "Magnesium Taurate": {
        numUnitsInServing: 1, 
        servingUnit: "caps",
    },
    "High Absorption Magnesium Glycinate 350": {
        numUnitsInServing: 350, 
        servingUnit: "mg",
    },
    "Iron Bisglycinate": {
        numUnitsInServing: 1, 
        servingUnit: "caps",
    },
    "Extend-Release Magnesium": {
        numUnitsInServing: 1, 
        servingUnit: "caps",
    },
    "Lutein & Zeaxanthin": {
        numUnitsInServing: 1, 
        servingUnit: "caps",
    },
    "Aged Garlic Extract": {
        numUnitsInServing: 600, 
        servingUnit: "mg",
    },
    "Organic Turmeric Curcumin": {
        numUnitsInServing: 2250, 
        servingUnit: "mg",
    },
    "Lithium Orotate Drops": {
        numUnitsInServing: .25, 
        servingUnit: "ml",
    },
    "Glycine": {
        numUnitsInServing: 1000, 
        servingUnit: "mg",
    },
    "Super K": {
        numUnitsInServing: 1500, 
        servingUnit: "mcg",
    },
};

let getNumBottles = orderEl => parseInt(orderEl
    .children[1]
    .children[0]
    .children[0]
    .children[1]
    .children[1]
    .innerText
    .split("Qty: ").slice(-1)[0]);

let SKIP_THESE = [
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

    let quantityText = parts.slice(-1)[0];
    let origQtyTxt = quantityText;
    if (quantityText.includes("(")) {
        quantityText = quantityText.match(/\((\d+)/).slice(-1)[0]
    }
    let quantityUnits = "caps";
    if (!["caps", "capsules", "tablets", "softgels", "vegcaps", "lozenges"].some(str => origQtyTxt.toLowerCase().includes(str))) {
        quantityUnits = origQtyTxt.match(/\(\d+ (.*)\)/).slice(-1)[0];
        console.log(quantityUnits);
    }
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
            ({ numUnitsInServing, servingUnit } = servingObj);
        }
    } else {
        [numUnitsInServing, servingUnit] = servingText.split(" ");
    }

    if (typeof numUnitsInServing !== "number") {
        numUnitsInServing = numUnitsInServing.replace(",", "");
    }
    let numUnitsInServingFinal = parseInt(numUnitsInServing);
    if (!numUnitsInServingFinal || numUnitsInServingFinal == 0 || name.includes(servingUnit)) {
        const servingObj = SERVINGS_LOOKUP[name];
        if (!servingObj) {
            throw {
                name: "servingError",
                level: "serious",
                message: `couldn't get serving info for ${name} '(${parts})'`,
                htmlMessage: this.message,
                toString: function(){return this.name + ": " + this.message;} 
            };
        }
        ({ numUnitsInServing: numUnitsInServingFinal, servingUnit } = servingObj);
    }

    return {
        orderDate: new Date(getDateOfOrder(ord)),
        name,
        quantity: parseInt(quantityText.split(" ")[0]),
        quantityUnits,
        servingUnit,
        numUnitsInServing: numUnitsInServingFinal,
        numBottles: getNumBottles(ord),
    }
}


function main(orderCutoffHuman, getFirst) {
    let orderEls;
    if (!getFirst) {
        const orderCutoff = Date.parse(orderCutoffHuman);
        orderEls = getOrderElements()
            .filter(el => !el.innerText.includes("Cancelled"))
            .filter(el => getDateOfOrder(el) > orderCutoff)
    } else {
        orderEls = [getOrderElements()[0]];
    }
    let suppEls = [];
    for (const orderEl of orderEls) {
        suppEls = suppEls.concat(getSupps(orderEl));
    }
    // TODO: write this to a file or copy to clipboard in CSV
    return suppEls.map(suppEl => makeSuppObj(suppEl)).filter(res => res != null);
}

console.log(JSON.stringify(main(null, true)));
