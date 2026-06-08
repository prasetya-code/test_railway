# NOTE

## stylelint -> linting untuk CSS

- instal stylelint -> `npm install --save-dev stylelint`
- tambahkan `.stylelintrc.json` sejajar dengan dir `node_modules`, berikut isi dari filenya:
```json
{
  "extends": [
    "stylelint-config-standard"
  ]
}
```

atau bisa di exetnd di package.json:
```json
"stylelint": {
    "extends": ["stylelint-config-standard"]
  },
```

- install configurasi lint sejajar dengan node_modules:
   `npm install --save-dev prettier stylelint-config-standard`

- jika sudah css lint sudah bisa digunakan