// Lädt content/*.js wie der Browser und gibt die Inhalte als JSON aus.
// Aufruf: node tools/dump-content.js > .data/content.json
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.join(__dirname, "..");
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
const files = [...html.matchAll(/<script src="(content\/[^"]+\.js)"><\/script>/g)].map((m) => m[1]);

const ctx = {};
vm.createContext(ctx);
for (const f of files) vm.runInContext(fs.readFileSync(path.join(root, f), "utf8"), ctx, { filename: f });
process.stdout.write(JSON.stringify(ctx.KROK, null, 1));
