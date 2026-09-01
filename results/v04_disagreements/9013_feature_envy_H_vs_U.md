# Smell occurrence 9013 — feature envy / major

- **Code under review:** `org.apache.solr.client.solrj.impl.Krb5HttpClientBuilder#setup Http2SolrClient`
- **Lines:** 124–130
- **Human label:** `H`
- **v04 label:** `U`

## Original LLM review (under test)

```
**Summary**

`Krb5HttpClientBuilder` is responsible for configuring HTTP clients (specifically for Solr) to support Kerberos (SPNEGO) authentication. It provides methods to set up authentication for both Apache HTTP and Jetty HTTP clients, manages a static JAAS configuration, and injects various authentication and cookie policies into the HTTP client builder. The class also contains a nested static class, `SolrJaasConfiguration`, which adapts the JAAS configuration to support custom app names.

**Review Comments**

---

**1. The `getBuilder(SolrHttpClientBuilder builder)` method is doing too much**

This method is responsible for a wide range of setup tasks: checking system properties, logging, setting system properties, configuring the global JAAS configuration, registering authentication and cookie providers, setting up a credentials provider, and adding a request interceptor. Each of these steps is a distinct responsibility, and the method currently spans over 60 lines.

This makes the method difficult to read, reason about, and maintain. For example, the logic for setting up the authentication scheme registry, the cookie spec registry, and the credentials provider could each be extracted into their own helper methods. This would allow the main method to read as a high-level orchestration of setup steps, improving clarity and making it easier to test or modify individual aspects of the setup.

**Suggestion:**  
Extract the following blocks into private helper methods:
- The logic for setting up the authentication scheme registry provider.
- The logic for setting up the cookie spec registry provider.
- The logic for setting up the default credentials provider.
- The logic for adding the request interceptor.

This will reduce the cognitive load for anyone reading or modifying the method and make the class easier to extend or debug in the future. See [Fowler: Extract Method](https://refactoring.com/catalog/extractMethod.html).

---

**2. The `createSPNEGOAuthentication()` method is tightly coupled to the details of JAAS configuration**

This method constructs a `SPNEGOAuthentication` instance and then proceeds to extract various options from the JAAS configuration entry, setting properties on the authentication object. The method is deeply concerned with the structure and semantics of the JAAS configuration, including knowledge of option keys like `"keyTab"`, `"principal"`, `"useTicketCache"`, and `"renewTGT"`.

This level of coupling suggests that the logic for interpreting JAAS configuration options might be better encapsulated elsewhere—potentially in a dedicated helper or even within the authentication object itself (if possible). As it stands, any changes to the JAAS configuration format or the set of supported options would require changes to this method, which is not ideal for maintainability.

**Suggestion:**  
Consider extracting the logic for interpreting JAAS configuration options into a separate helper class or method. Alternatively, if the authentication object can be constructed with a configuration map, delegate the responsibility for interpreting these options to that object.

---

**3. The `SolrJaasConfiguration` class is almost a pure data holder with minimal behavior**

The nested `SolrJaasConfiguration` class primarily wraps another JAAS `Configuration` and delegates calls to it, with a small amount of logic to substitute the app name for certain known values. Aside from this, it holds a set of app names and a reference to the base configuration.

While it does have a small amount of logic, the class is mostly a thin wrapper and does not encapsulate much behavior. If more logic is added in the future, it may be justified as a full-fledged class, but as it stands, it is close to being a data holder with a single method override.

**Suggestion:**  
If additional behavior is not anticipated, consider whether this class could be replaced with a more focused method or a lambda. If it is expected to grow, consider adding more responsibility to it (such as validation or transformation of configuration entries) to justify its existence as a class.

---

**4. The static field `jaasConfig` and its lifecycle management are awkwardly handled**

The static field `jaasConfig` is initialized once and can be reset via `regenerateJaasConfiguration()`, which is noted as "not thread safe" and "only used for tests." This pattern can lead to subtle bugs, especially in concurrent or multi-test environments, as the configuration is global and mutable.

While this is not strictly a code smell in the sense of the requested categories, it does indicate that the class is holding global mutable state, which can make reasoning about its behavior more difficult, especially in tests.

**Suggestion:**  
If possible, avoid static mutable state. If it must be present, document its lifecycle and usage patterns clearly, and consider using dependency injection or instance-level configuration to avoid global state.

---

**5. The class as a whole is highly procedural and orchestrates many details directly**

`Krb5HttpClientBuilder` is responsible for a wide range of setup and configuration tasks, many of which involve direct manipulation of system properties, global configuration, and low-level HTTP client details. This results in a class that is more procedural than object-oriented, with many responsibilities that could be delegated to collaborators or helpers.

While this may be necessary due to the nature of the integration, it does make the class harder to test and maintain, as changes to one aspect of the setup may have unintended consequences elsewhere.

**Suggestion:**  
Where possible, delegate responsibilities to helper classes or methods, and strive to keep each method focused on a single aspect of the setup process. This will improve cohesion and make the class easier to evolve over time.

---

**Summary**

The main concern in this file is the presence of long, multi-responsibility methods (notably `getBuilder(SolrHttpClientBuilder builder)`) and procedural logic that could be better decomposed into smaller, focused helpers. There is also some evidence of classes and methods that are more interested in the details of other objects (such as JAAS configuration parsing), which could be refactored for better encapsulation. The nested configuration class is close to being a data holder, and the use of static mutable state is a potential source of confusion.

Refactoring to extract methods, delegate responsibilities, and clarify ownership of logic would improve maintainability and readability.
```

## v04 judge reasoning (REASONING + CLASSIFICATION + JUSTIFICATION)

```
REASONING:
  Step 1 (TYPE): mentions "Feature Envy" only generically ("more interested in the details of other objects"), but does not use the canonical name or synonym directly for the targeted snippet.
  Step 5 (DIFFERENT-SMELL): identifies "Long Method" as the main concern, specifically in `getBuilder(SolrHttpClientBuilder builder)`, which is plausible in the file context.

CLASSIFICATION: U

JUSTIFICATION: The response does not name Feature Envy (the target smell) in the targeted snippet, but instead focuses on Long Method elsewhere and only generically alludes to Feature Envy, so it is classified as Uncertain due to plausible identification of a different smell.
```