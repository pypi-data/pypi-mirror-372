from cardlink.methods.billPayments import billPayments
from cardlink.methods.billStatus import billStatus
from cardlink.methods.createBill import createBill
from cardlink.methods.createFullRefund import createFullRefund
from cardlink.methods.createPartialRefund import createPartialRefund
from cardlink.methods.createPersonalPayout import createPersonalPayout
from cardlink.methods.createRegularPayout import createRegularPayoutCreditCard, createPersonalPayoutSBP, createPersonalPayoutSteam, createPersonalPayoutCrypto
from cardlink.methods.getBalance import getBalance
from cardlink.methods.getBanks import getBanks
from cardlink.methods.paymentStatus import paymentStatus
from cardlink.methods.payoutStatus import payoutStatus
from cardlink.methods.refundStatus import refundStatus
from cardlink.methods.searchBill import searchBill
from cardlink.methods.searchPayments import searchPayments
from cardlink.methods.searchPayout import searchPayout
from cardlink.methods.searchRefund import searchRefund
from cardlink.methods.toggleActivity import toggleActivity
from cardlink.methods.base import CardLinkBaseMethod


class Methods(
    billPayments,
    billStatus,
    createBill,
    createFullRefund,
    createPartialRefund,
    createPersonalPayout,
    createRegularPayoutCreditCard, createPersonalPayoutSBP, createPersonalPayoutSteam, createPersonalPayoutCrypto,
    getBalance,
    getBanks,
    paymentStatus,
    payoutStatus,
    refundStatus,
    searchBill,
    searchPayout,
    searchPayments,
    searchRefund,
    toggleActivity
):
    pass


__all__ = [
    "CardLinkBaseMethod"
]
