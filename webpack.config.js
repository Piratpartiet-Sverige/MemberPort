const path = require('path')
const fs = require('fs')
const MiniCSSExtractPlugin = require('mini-css-extract-plugin')

const isDev = process.env.NODE_ENV === 'development'

const tsRegex = /\.tsx?$/
const assetRegex = /\.(png|jpg|gif|eot|svg|ttf|woff|woff2|otf)$/

function walk (dir) {
  let results = []
  const list = fs.readdirSync(dir)
  list.forEach(function (file) {
    file = path.join(dir, file)
    const stat = fs.statSync(file)
    if (stat && stat.isDirectory()) results = results.concat(walk(file))
    else results.push(file)
  })
  return results.map((file) => `./${file}`)
}

function dirname (file) {
  const relative = path.relative('./assets/ts/entrypoints', file)
  const ext = path.extname(file)

  return relative.replace(ext, '')
}

const entryPoints = walk('./assets/ts/entrypoints').reduce((acc, cur) => {
  const ext = path.extname(cur)
  const directory = dirname(cur)

  if (tsRegex.test(ext) ||assetRegex.test(ext)) {
    acc[directory] ? acc[directory].push(cur) : acc[directory] = [ cur ]
  }

  return acc
}, {})

module.exports = {
  mode: 'production',
  entry: entryPoints,
  output: {
    filename: '[name].bundle.js',
    path: path.join(__dirname, 'static')
  },

  // Enable sourcemaps for debugging webpack's output.
  devtool: 'source-map',

  resolve: {
    // Add '.ts' and '.tsx' as resolvable extensions.
    extensions: ['.ts', '.tsx', '.js', '.json']
  },
  module: {
    rules: [
      // All files with a '.ts' or '.tsx' extension will be handled by 'awesome-typescript-loader'.
      {
        test: /\.tsx?$/,
        use: [
          {
            loader: 'ts-loader'
          }
        ],
        exclude: /node_modules/
      },
      {
        test: /\.(sa|sc|c)ss$/,
        use: [
          isDev ? 'style-loader' : MiniCSSExtractPlugin.loader,
          'css-loader',
          'sass-loader'
        ]
      },
      {
        test: /\.(png|svg|woff|woff2|eot|ttf|otf)$/,
        loader: 'url-loader',
        options: {
          name: 'assets/[name].[hash].[ext]',
          silent: true
        }
      }
    ]
  },
  plugins: [
    new MiniCSSExtractPlugin({
      filename: 'css/[name].bundle.css'
    })
  ]
}
