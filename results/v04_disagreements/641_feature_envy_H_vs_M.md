# Smell occurrence 641 — feature envy / critical

- **Code under review:** `org.apache.zookeeper.server.auth.KerberosName.Rule.replaceSubstitution String|Pattern|String|boolean`
- **Lines:** 287–295
- **Human label:** `H`
- **v04 label:** `M`

## Original LLM review (under test)

```
**Summary**

The `KerberosName` class is responsible for parsing Kerberos principal names, breaking them into components (service, host, realm), and translating them into local operating system usernames according to configurable rules. It encapsulates both the parsing logic and the rule-based translation, including static configuration and error handling. The class also contains a nested static `Rule` class that models individual translation rules and their application.

**Review Comments**

---

**1. The `getShortName` Method is Doing Too Much**

The `getShortName` method is responsible for translating a Kerberos principal into a local username. While the method is not excessively long in terms of lines, it is orchestrating several distinct responsibilities:

- It determines how to construct the `params` array based on the presence or absence of `hostName` and `realm`.
- It iterates over the static `rules` list, applying each rule in turn.
- It handles the fallback and error case if no rule matches.

This method is mixing the logic of parameter construction, rule application, and error handling. This makes it harder to test or modify any one aspect in isolation. For example, the logic for constructing the `params` array could be extracted into a helper method (e.g., `buildParams()`), and the rule application loop could be separated into another method (e.g., `applyRules(params)`). This would make the intent of each step clearer and reduce the cognitive load for future maintainers.

*Suggestion*: Extract the parameter construction and rule application into separate private methods. This will clarify the high-level flow and make the method easier to read and maintain. See Fowler's "Extract Method" refactoring: https://refactoring.com/catalog/extractMethod.html

---

**2. The `Rule` Class Encapsulates Both Data and Behavior Appropriately**

The nested static `Rule` class is not a passive data holder; it encapsulates both the data for a rule and the logic for applying it. This is a good example of keeping data and behavior together, and avoids the "data class" smell. No issues here.

---

**3. Potential for Feature Envy in the `Rule.apply` Method**

Within the `Rule.apply` method, the logic is tightly coupled to the structure of the `params` array, which is constructed externally in `KerberosName.getShortName`. The method expects the first element to be the realm, and subsequent elements to be the service and host. This tight coupling means that any change to how `params` is constructed in `KerberosName` must be mirrored in `Rule`, and vice versa.

While this is not a classic case of feature envy (since `Rule` is a static inner class and the protocol is well-defined), it does suggest that the logic for parameter construction and validation could be more robustly encapsulated. For example, instead of passing a raw array, a small value object representing the parsed principal could be passed, making the contract clearer and less error-prone.

*Suggestion*: Consider introducing a value object (e.g., `PrincipalComponents`) to encapsulate the realm, service, and host, and pass this to `Rule.apply`. This would clarify the contract and reduce the risk of mismatches.

---

**4. The Class is Not a Data Class**

`KerberosName` is not a passive data holder; it encapsulates parsing, rule management, and translation logic. The fields are private and final, and the class provides behavior beyond simple getters/setters. No issues here.

---

**5. Static State and Configuration Management**

The class uses static fields (`rules`, `defaultRealm`) and a static initializer to manage configuration. While this is not directly a code smell in the context of the requested review, it does mean that the class is globally stateful and not easily testable in isolation. If the rules or default realm need to change at runtime or for testing, this could lead to subtle bugs or test pollution.

*Suggestion*: If feasible, consider refactoring to allow instance-level configuration, or at least provide a way to reset or override the static configuration for testing purposes.

---

**6. The `main` Method is a Utility/Test Harness**

The `main` method is a simple utility for manual testing. No issues related to the target smells.

---

**Summary**

Overall, the class is well-structured and encapsulates both data and behavior appropriately. The main area for improvement is the `getShortName` method, which could be decomposed for clarity and maintainability. The coupling between parameter construction and rule application could also be improved by introducing a value object to represent principal components. No issues with data classes or classic feature envy were found.
```

## v04 judge reasoning (REASONING + CLASSIFICATION + JUSTIFICATION)

```
REASONING:
  Step 6 (NEGATIVE-SIGNAL): denies any smell ("No issues with data classes or classic feature envy were found.")

CLASSIFICATION: M

JUSTIFICATION: The response explicitly denies the presence of Feature Envy (the confirmed oracle smell) in the targeted snippet, which is misleading.
```