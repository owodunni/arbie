var Token = artifacts.require("Token");

module.exports = function(deployer) {
  deployer.deploy(Token, "Eth", "WTH", 10);
};
