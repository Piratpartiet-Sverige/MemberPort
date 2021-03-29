const path = require('path')
const MiniCSSExtractPlugin = require('mini-css-extract-plugin')

const isDev = process.env.NODE_ENV === 'development'

module.exports = {
  mode: 'production',
  entry: {
    client: ['./assets/ts/app.ts']
  },
  output: {
    filename: '[name].bundle.js',
    path: path.join(__dirname, '/static/js')
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
            loader: 'awesome-typescript-loader',
            options: {
              useCache: true,
              silent: true
            }
          }
        ]
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
      //filename: 'css/[name].[contenthash].bundle.css'
      filename: '../css/[name].bundle.css'
    })
  ]
}
