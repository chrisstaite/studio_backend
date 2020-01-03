const path = require("path");

module.exports = {
  entry: "./index.js",
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "bundle.js"
  },
  devtool: 'source-map',
  mode: process.env.DEV === "true" ? 'development' : 'production',
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-react'],
          }
        }
      }
    ]
  }
};