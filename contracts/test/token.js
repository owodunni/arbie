const Token = artifacts.require("Token");

contract("Token", accounts => {
  it("should put 10 Token in the first account", () =>
    Token.deployed()
      .then(instance => instance.balanceOf.call(accounts[0]))
          .then(balance => {
            assert.equal(
              balance.valueOf(),
              10,
              "10 wasn't in the first account"
            );
          }));
});
