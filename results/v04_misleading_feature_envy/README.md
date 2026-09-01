# Casos Misleading do v04 — Feature Envy

Total: **31 casos**. Cada arquivo .md contém: review original do LLM-under-test (gpt-4.1) + reasoning completo do v04 explicando por que classificou como Misleading.

Ordem: por `smell_occurrence_id`.

| # | smell_occ | severity | code_name |
|---|-----------|----------|-----------|
|  1 | [622](00622_org.apache.zookeeper.graph.JsonGenerator.JsonGenerator_LogIterator.md) | major | `org.apache.zookeeper.graph.JsonGenerator.JsonGenerator LogIterato` |
|  2 | [641](00641_org.apache.zookeeper.server.auth.KerberosName.Rule.replaceSubstitution_String_Pa.md) | critical | `org.apache.zookeeper.server.auth.KerberosName.Rule.replaceSubstit` |
|  3 | [761](00761_org.eclipse.kapua.service.authorization.group.shiro.GroupServiceImpl_onKapuaEven.md) | major | `org.eclipse.kapua.service.authorization.group.shiro.GroupServiceI` |
|  4 | [805](00805_org.eclipse.orion.server.cf.loggregator.LoggregatorMessage.Message.Builder_merge.md) | major | `org.eclipse.orion.server.cf.loggregator.LoggregatorMessage.Messag` |
|  5 | [1952](01952_org.apache.accumulo.server.util.ListVolumesUsed.listZookeeper_ServerContext.md) | major | `org.apache.accumulo.server.util.ListVolumesUsed.listZookeeper Ser` |
|  6 | [3061](03061_com.oracle.bmc.budget.model.CreateBudgetDetails.Builder_build.md) | critical | `com.oracle.bmc.budget.model.CreateBudgetDetails.Builder#build` |
|  7 | [3063](03063_org.apache.tinkerpop.gremlin.process.traversal.util.TraversalUtil.applyAll_S_Tra.md) | major | `org.apache.tinkerpop.gremlin.process.traversal.util.TraversalUtil` |
|  8 | [3845](03845_org.apache.commons.beanutils2.PropertyUtils.getPropertyEditorClass_Object_String.md) | critical | `org.apache.commons.beanutils2.PropertyUtils.getPropertyEditorClas` |
|  9 | [3877](03877_com.google.javascript.rhino.jstype.AllType_recursionUnsafeHashCode.md) | major | `com.google.javascript.rhino.jstype.AllType#recursionUnsafeHashCod` |
| 10 | [3904](03904_org.apache.cayenne.exp.parser.ASTEqual.evaluateImpl_Object_Object.md) | major | `org.apache.cayenne.exp.parser.ASTEqual.evaluateImpl Object|Object` |
| 11 | [4060](04060_org.apache.isis.schema.services.jaxb.JaxbServiceDefault_configure_Marshaller.md) | major | `org.apache.isis.schema.services.jaxb.JaxbServiceDefault#configure` |
| 12 | [4255](04255_org.apache.cxf.wsn.client.CreatePullPoint_create_String.md) | major | `org.apache.cxf.wsn.client.CreatePullPoint#create String` |
| 13 | [5129](05129_org.eclipse.tycho.p2.target.filters.TargetPlatformFilterEvaluator.DebugFilterLog.md) | major | `org.eclipse.tycho.p2.target.filters.TargetPlatformFilterEvaluator` |
| 14 | [5410](05410_org.apache.directory.api.ldap.model.schema.registries.ImmutableComparatorRegistr.md) | major | `org.apache.directory.api.ldap.model.schema.registries.ImmutableCo` |
| 15 | [5666](05666_org.eclipse.birt.core.fs.LocalFile_mkdirs.md) | major | `org.eclipse.birt.core.fs.LocalFile#mkdirs` |
| 16 | [5787](05787_org.apache.poi.xssf.model.TestCommentsTable_writeRead.md) | major | `org.apache.poi.xssf.model.TestCommentsTable#writeRead` |
| 17 | [6154](06154_org.apache.asterix.dataflow.data.nontagged.serde.AGeometrySerializerDeserializer.md) | major | `org.apache.asterix.dataflow.data.nontagged.serde.AGeometrySeriali` |
| 18 | [6390](06390_org.eclipse.birt.report.designer.ui.ide.navigator.GenerateDocumentAction_run_IAc.md) | major | `org.eclipse.birt.report.designer.ui.ide.navigator.GenerateDocumen` |
| 19 | [8254](08254_org.apache.commons.net.discard.DiscardUDPClient_send_byte_int_InetAddress_int.md) | major | `org.apache.commons.net.discard.DiscardUDPClient#send byte[]|int|I` |
| 20 | [8527](08527_jdk.management.jfr.ConfigurationInfo.ConfigurationInfo_CompositeData.md) | major | `jdk.management.jfr.ConfigurationInfo.ConfigurationInfo CompositeD` |
| 21 | [9274](09274_org.apache.flink.graph.types.valuearray.DoubleValueArray_write_DataOutputView.md) | major | `org.apache.flink.graph.types.valuearray.DoubleValueArray#write Da` |
| 22 | [9351](09351_sun.nio.fs.WindowsSecurity.openProcessToken_int.md) | critical | `sun.nio.fs.WindowsSecurity.openProcessToken int` |
| 23 | [9477](09477_org.apache.pig.PigServer.PigServer_PigContext_boolean.md) | major | `org.apache.pig.PigServer.PigServer PigContext|boolean` |
| 24 | [9728](09728_com.facebook.buck.core.model.impl.InMemoryBuildFileTree.collectBasePaths_Iterabl.md) | major | `com.facebook.buck.core.model.impl.InMemoryBuildFileTree.collectBa` |
| 25 | [10606](10606_org.graalvm.visualvm.lib.profiler.snaptracer.impl.timeline.TimelineXYPainter_get.md) | major | `org.graalvm.visualvm.lib.profiler.snaptracer.impl.timeline.Timeli` |
| 26 | [10700](10700_com.facebook.buck.cli.AuditRulesCommand_runWithoutHelp_CommandRunnerParams.md) | major | `com.facebook.buck.cli.AuditRulesCommand#runWithoutHelp CommandRun` |
| 27 | [10804](10804_org.apache.qpid.server.security.access.config.AclFileParser.parse_Reader_EventLo.md) | major | `org.apache.qpid.server.security.access.config.AclFileParser.parse` |
| 28 | [10919](10919_org.apache.camel.component.disruptor.DisruptorComponent_createEndpoint_String_St.md) | major | `org.apache.camel.component.disruptor.DisruptorComponent#createEnd` |
| 29 | [12805](12805_org.eclipse.elk.alg.radial.options._create.md) | major | `org.eclipse.elk.alg.radial.options.#create` |
| 30 | [14835](14835_org.apache.fop.svg.AbstractFOPImageElementBridge_createImageGraphicsNode_BridgeC.md) | major | `org.apache.fop.svg.AbstractFOPImageElementBridge#createImageGraph` |
| 31 | [15149](15149_org.apache.aries.spifly.statictool.Main.weaveDir_File_String_String_String.md) | major | `org.apache.aries.spifly.statictool.Main.weaveDir File|String|Stri` |