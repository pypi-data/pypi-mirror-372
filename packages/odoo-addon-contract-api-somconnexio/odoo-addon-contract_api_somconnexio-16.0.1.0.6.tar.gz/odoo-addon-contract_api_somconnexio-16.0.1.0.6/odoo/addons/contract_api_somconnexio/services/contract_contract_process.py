from odoo import models


class ErrorUnsuportedTechnology(Exception):
    pass


class ContractContractProcess(models.AbstractModel):
    _name = "contract.contract.process"
    _register = True
    _description = """
      ContractContractProcess --> ContractProcessFactory

      Refactor to separate the methods of contracts in classes with type as scope.
      We create the ADSLContractProcess, FiberContractProcess,
      MobileContractProcess and Router4GContractProcess classes.

        BaseContractProcess
               |
               |
        ---------------------------
        |                         |
    MobileContractProcess         |
                          BAContractProcess
                                  |
                -------------------------------------
                |                 |                 |
        ADSLContractProcess       |     Router4GContractProcess
                                  |
                           FiberContractProcess
    """

    # pylint: disable=W8106
    def create(self, **params):
        Contract = None
        service_technology = params["service_technology"]
        if service_technology == "Mobile":
            Contract = self.env["mobile.contract.process"]
        elif service_technology == "ADSL":
            Contract = self.env["adsl.contract.process"]
        elif service_technology == "Fiber":
            Contract = self.env["fiber.contract.process"]
        elif service_technology == "4G":
            Contract = self.env["router.4g.contract.process"]
        elif service_technology == "Switchboard":
            Contract = self.env["sb.contract.process"]
        else:
            raise ErrorUnsuportedTechnology()

        return Contract.sudo().create(**params)
