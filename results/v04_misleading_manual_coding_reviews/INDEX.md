# Index of the 69 Misleading items (v04) — manual coding reference

Companion to [`../v04_misleading_manual_coding.csv`](../v04_misleading_manual_coding.csv).
Each file contains: the annotated sample (oracle granularity), the full review produced by the
gpt-4.1 under test, and the full reasoning of the v04 judge.

The 35 Data Class and the 3 Long Method items live in this directory. The 31 Feature Envy items
already existed under `results/v04_misleading_feature_envy/` and are linked from here (those files
do not include the annotated sample; physical line counts are in the CSV column `snippet_lines`).

Column headings below mirror the `author_*` columns of the CSV.

| occ | smell | severity | lines | author_denial_type | long method main issue | oracle inconsistent | judge error | file |
|-----|-------|----------|-------|------------|------------------------|---------------------|-------------|------|
| 719 | data class | critical | 118 | with_reason | no | no | no | [00719_org.eclipse.hono.config.SignatureSuppo…](00719_org.eclipse.hono.config.SignatureSupportingConfigProperties.md) |
| 732 | data class | major | 279 | with_reason | no | no | no | [00732_org.eclipse.ice.reactor.plant.Subchann…](00732_org.eclipse.ice.reactor.plant.Subchannel.md) |
| 866 | data class | major | 36 | with_reason | no | **yes** | no | [00866_org.eclipse.vorto.repository.importer.…](00866_org.eclipse.vorto.repository.importer.ipso.ObjectFactory.md) |
| 1048 | data class | major | 62 | with_reason | no | no | no | [01048_com.google.j2cl.ast.FieldDescriptor.Bu…](01048_com.google.j2cl.ast.FieldDescriptor.Builder.md) |
| 1103 | data class | critical | 47 | with_reason | no | **yes** | no | [01103_javax.xml.xpath.XPathConstants.md…](01103_javax.xml.xpath.XPathConstants.md) |
| 2023 | data class | major | 54 | with_reason | no | no | no | [02023_org.apache.atlas.utils.AtlasPerfTracer…](02023_org.apache.atlas.utils.AtlasPerfTracer.md) |
| 2035 | data class | major | 78 | with_reason | no | no | no | [02035_org.apache.cloudstack.api.command.admi…](02035_org.apache.cloudstack.api.command.admin.ca.RevokeCertificateCmd.md) |
| 3605 | data class | critical | 3 | with_reason | no | **yes** | no | [03605_org.apache.rocketmq.common.constant.DB…](03605_org.apache.rocketmq.common.constant.DBMsgConstants.md) |
| 3707 | data class | major | 6 | with_reason | no | **yes** | no | [03707_org.apache.camel.component.infinispan.…](03707_org.apache.camel.component.infinispan.embedded.InfinispanAsyncLocalEventListener.md) |
| 4118 | data class | major | 72 | with_reason | **yes** | no | no | [04118_org.apache.storm.stats.BoltExecutorSta…](04118_org.apache.storm.stats.BoltExecutorStats.md) |
| 4240 | data class | major | 482 | no_reason | **yes** | no | no | [04240_org.apache.maven.scm.provider.perforce…](04240_org.apache.maven.scm.provider.perforce.PerforceScmProvider.md) |
| 4284 | data class | major | 146 | with_reason | no | no | no | [04284_org.apache.jena.sparql.expr.ExprList.m…](04284_org.apache.jena.sparql.expr.ExprList.md) |
| 4439 | data class | critical | 13 | with_reason | no | **yes** | no | [04439_org.apache.cayenne.template.parser.Exp…](04439_org.apache.cayenne.template.parser.ExpressionNode.md) |
| 5190 | data class | major | 26 | with_reason | no | no | no | [05190_org.apache.commons.jelly.tags.define.T…](05190_org.apache.commons.jelly.tags.define.TagTag.md) |
| 5550 | data class | major | 49 | with_reason | no | no | no | [05550_org.springframework.security.access.in…](05550_org.springframework.security.access.intercept.aopalliance.MethodSecurityIntercep.md) |
| 5553 | data class | critical | 35 | with_reason | no | **yes** | no | [05553_org.springframework.ide.eclipse.aop.co…](05553_org.springframework.ide.eclipse.aop.core.model.IAopReferenceModel.md) |
| 5796 | data class | critical | 45 | with_reason | no | no | no | [05796_org.springframework.web.context.suppor…](05796_org.springframework.web.context.support.ServletContextAttributeFactoryBean.md) |
| 5805 | data class | critical | 78 | with_reason | no | **yes** | no | [05805_org.apache.cxf.jaxrs.rx2.client.Flowab…](05805_org.apache.cxf.jaxrs.rx2.client.FlowableRxInvoker.md) |
| 5930 | data class | major | 41 | with_reason | no | **yes** | no | [05930_org.apache.tinkerpop.gremlin.structure…](05930_org.apache.tinkerpop.gremlin.structure.Property.Exceptions.md) |
| 6254 | data class | major | 141 | with_reason | **yes** | no | no | [06254_com.epam.wilma.service.configuration.S…](06254_com.epam.wilma.service.configuration.StubConfiguration.md) |
| 6363 | data class | critical | 203 | with_reason | **yes** | no | no | [06363_org.apache.drill.common.expression.fn.…](06363_org.apache.drill.common.expression.fn.JodaDateValidator.md) |
| 6405 | data class | critical | 203 | with_reason | **yes** | no | no | [06405_com.google.j2cl.common.Problems.md…](06405_com.google.j2cl.common.Problems.md) |
| 6424 | data class | major | 59 | with_reason | no | no | no | [06424_org.apache.flink.runtime.jobmaster.fac…](06424_org.apache.flink.runtime.jobmaster.factories.DefaultJobMasterServiceFactory.md) |
| 7110 | data class | major | 56 | with_reason | no | no | no | [07110_org.apache.sis.internal.jaxb.code.DQ_E…](07110_org.apache.sis.internal.jaxb.code.DQ_EvaluationMethodTypeCode.md) |
| 7611 | data class | major | 89 | with_reason | no | **yes** | no | [07611_org.springframework.statemachine.regio…](07611_org.springframework.statemachine.region.Region.md) |
| 7686 | data class | major | 92 | with_reason | **yes** | no | no | [07686_org.apache.skywalking.oap.server.core.…](07686_org.apache.skywalking.oap.server.core.analysis.data.LimitedSizeDataCollection.md) |
| 9748 | data class | critical | 36 | with_reason | no | **yes** | no | [09748_org.eclipse.texlipse.builder.XelatexRu…](09748_org.eclipse.texlipse.builder.XelatexRunner.md) |
| 10284 | data class | critical | 40 | with_reason | no | no | no | [10284_org.eclipse.jetty.util.ProcessorUtils.…](10284_org.eclipse.jetty.util.ProcessorUtils.md) |
| 10360 | data class | major | 58 | with_reason | no | no | no | [10360_com.ibm.dtfj.corereaders.zos.util.Obje…](10360_com.ibm.dtfj.corereaders.zos.util.ObjectLruCache.md) |
| 10618 | data class | critical | 13 | with_reason | no | no | no | [10618_org.apache.cloudstack.api.response.Dep…](10618_org.apache.cloudstack.api.response.DeploymentPlannersResponse.md) |
| 10632 | data class | critical | 7 | no_reason | **yes** | no | no | [10632_org.apache.hadoop.mapreduce.task.Reduc…](10632_org.apache.hadoop.mapreduce.task.ReduceContextImpl.ValueIterable.md) |
| 11149 | data class | major | 27 | not_discussed | **yes** | no | no | [11149_com.oracle.truffle.api.TruffleFile.Wal…](11149_com.oracle.truffle.api.TruffleFile.Walker.Event.md) |
| 11205 | data class | major | 387 | with_reason | no | no | no | [11205_ms.tfs.workitemtracking.configurations…](11205_ms.tfs.workitemtracking.configurationsettingsservice._03._ConfigurationSettingsS.md) |
| 13785 | data class | major | 48 | with_reason | no | no | no | [13785_org.apache.royale.compiler.ant.config.…](13785_org.apache.royale.compiler.ant.config.ConfigBoolean.md) |
| 15059 | data class | critical | 56 | with_reason | no | no | no | [15059_org.springframework.aop.support.Static…](15059_org.springframework.aop.support.StaticMethodMatcherPointcutAdvisor.md) |
| 622 | feature envy | major | 139 | no_reason | **yes** | no | no | [00622_org.apache.zookeeper.graph.JsonGenerat…](../v04_misleading_feature_envy/00622_org.apache.zookeeper.graph.JsonGenerator.JsonGenerator_LogIterator.md) |
| 641 | feature envy | critical | 9 | no_reason | **yes** | no | no | [00641_org.apache.zookeeper.server.auth.Kerbe…](../v04_misleading_feature_envy/00641_org.apache.zookeeper.server.auth.KerberosName.Rule.replaceSubstitution_String_Pa.md) |
| 761 | feature envy | major | 10 | with_reason | **yes** | no | no | [00761_org.eclipse.kapua.service.authorizatio…](../v04_misleading_feature_envy/00761_org.eclipse.kapua.service.authorization.group.shiro.GroupServiceImpl_onKapuaEven.md) |
| 805 | feature envy | major | 66 | with_reason | no | no | no | [00805_org.eclipse.orion.server.cf.loggregato…](../v04_misleading_feature_envy/00805_org.eclipse.orion.server.cf.loggregator.LoggregatorMessage.Message.Builder_merge.md) |
| 1952 | feature envy | major | 15 | with_reason | **yes** | no | no | [01952_org.apache.accumulo.server.util.ListVo…](../v04_misleading_feature_envy/01952_org.apache.accumulo.server.util.ListVolumesUsed.listZookeeper_ServerContext.md) |
| 3061 | feature envy | critical | 14 | with_reason | no | no | no | [03061_com.oracle.bmc.budget.model.CreateBudg…](../v04_misleading_feature_envy/03061_com.oracle.bmc.budget.model.CreateBudgetDetails.Builder_build.md) |
| 3063 | feature envy | major | 5 | with_reason | no | no | no | [03063_org.apache.tinkerpop.gremlin.process.t…](../v04_misleading_feature_envy/03063_org.apache.tinkerpop.gremlin.process.traversal.util.TraversalUtil.applyAll_S_Tra.md) |
| 3845 | feature envy | critical | 7 | with_reason | no | no | no | [03845_org.apache.commons.beanutils2.Property…](../v04_misleading_feature_envy/03845_org.apache.commons.beanutils2.PropertyUtils.getPropertyEditorClass_Object_String.md) |
| 3877 | feature envy | major | 4 | with_reason | no | **yes** | no | [03877_com.google.javascript.rhino.jstype.All…](../v04_misleading_feature_envy/03877_com.google.javascript.rhino.jstype.AllType_recursionUnsafeHashCode.md) |
| 3904 | feature envy | major | 22 | with_reason | **yes** | no | no | [03904_org.apache.cayenne.exp.parser.ASTEqual…](../v04_misleading_feature_envy/03904_org.apache.cayenne.exp.parser.ASTEqual.evaluateImpl_Object_Object.md) |
| 4060 | feature envy | major | 7 | with_reason | **yes** | no | no | [04060_org.apache.isis.schema.services.jaxb.J…](../v04_misleading_feature_envy/04060_org.apache.isis.schema.services.jaxb.JaxbServiceDefault_configure_Marshaller.md) |
| 4255 | feature envy | major | 7 | with_reason | no | no | no | [04255_org.apache.cxf.wsn.client.CreatePullPo…](../v04_misleading_feature_envy/04255_org.apache.cxf.wsn.client.CreatePullPoint_create_String.md) |
| 5129 | feature envy | major | 5 | not_discussed | **yes** | no | **yes** | [05129_org.eclipse.tycho.p2.target.filters.Ta…](../v04_misleading_feature_envy/05129_org.eclipse.tycho.p2.target.filters.TargetPlatformFilterEvaluator.DebugFilterLog.md) |
| 5410 | feature envy | major | 5 | with_reason | no | no | no | [05410_org.apache.directory.api.ldap.model.sc…](../v04_misleading_feature_envy/05410_org.apache.directory.api.ldap.model.schema.registries.ImmutableComparatorRegistr.md) |
| 5666 | feature envy | major | 5 | with_reason | no | no | no | [05666_org.eclipse.birt.core.fs.LocalFile_mkd…](../v04_misleading_feature_envy/05666_org.eclipse.birt.core.fs.LocalFile_mkdirs.md) |
| 5787 | feature envy | major | 48 | with_reason | **yes** | no | no | [05787_org.apache.poi.xssf.model.TestComments…](../v04_misleading_feature_envy/05787_org.apache.poi.xssf.model.TestCommentsTable_writeRead.md) |
| 6154 | feature envy | major | 13 | with_reason | **yes** | no | no | [06154_org.apache.asterix.dataflow.data.nonta…](../v04_misleading_feature_envy/06154_org.apache.asterix.dataflow.data.nontagged.serde.AGeometrySerializerDeserializer.md) |
| 6390 | feature envy | major | 49 | with_reason | **yes** | no | no | [06390_org.eclipse.birt.report.designer.ui.id…](../v04_misleading_feature_envy/06390_org.eclipse.birt.report.designer.ui.ide.navigator.GenerateDocumentAction_run_IAc.md) |
| 8254 | feature envy | major | 9 | with_reason | no | no | no | [08254_org.apache.commons.net.discard.Discard…](../v04_misleading_feature_envy/08254_org.apache.commons.net.discard.DiscardUDPClient_send_byte_int_InetAddress_int.md) |
| 8527 | feature envy | major | 8 | with_reason | no | no | no | [08527_jdk.management.jfr.ConfigurationInfo.C…](../v04_misleading_feature_envy/08527_jdk.management.jfr.ConfigurationInfo.ConfigurationInfo_CompositeData.md) |
| 9274 | feature envy | major | 8 | not_discussed | **yes** | no | no | [09274_org.apache.flink.graph.types.valuearra…](../v04_misleading_feature_envy/09274_org.apache.flink.graph.types.valuearray.DoubleValueArray_write_DataOutputView.md) |
| 9351 | feature envy | critical | 7 | with_reason | **yes** | no | no | [09351_sun.nio.fs.WindowsSecurity.openProcess…](../v04_misleading_feature_envy/09351_sun.nio.fs.WindowsSecurity.openProcessToken_int.md) |
| 9477 | feature envy | major | 74 | with_reason | **yes** | no | no | [09477_org.apache.pig.PigServer.PigServer_Pig…](../v04_misleading_feature_envy/09477_org.apache.pig.PigServer.PigServer_PigContext_boolean.md) |
| 9728 | feature envy | major | 5 | no_reason | no | no | **yes** | [09728_com.facebook.buck.core.model.impl.InMe…](../v04_misleading_feature_envy/09728_com.facebook.buck.core.model.impl.InMemoryBuildFileTree.collectBasePaths_Iterabl.md) |
| 10606 | feature envy | major | 14 | with_reason | no | no | no | [10606_org.graalvm.visualvm.lib.profiler.snap…](../v04_misleading_feature_envy/10606_org.graalvm.visualvm.lib.profiler.snaptracer.impl.timeline.TimelineXYPainter_get.md) |
| 10700 | feature envy | major | 59 | with_reason | **yes** | no | no | [10700_com.facebook.buck.cli.AuditRulesComman…](../v04_misleading_feature_envy/10700_com.facebook.buck.cli.AuditRulesCommand_runWithoutHelp_CommandRunnerParams.md) |
| 10804 | feature envy | major | 137 | with_reason | **yes** | no | no | [10804_org.apache.qpid.server.security.access…](../v04_misleading_feature_envy/10804_org.apache.qpid.server.security.access.config.AclFileParser.parse_Reader_EventLo.md) |
| 10919 | feature envy | major | 45 | with_reason | **yes** | no | no | [10919_org.apache.camel.component.disruptor.D…](../v04_misleading_feature_envy/10919_org.apache.camel.component.disruptor.DisruptorComponent_createEndpoint_String_St.md) |
| 12805 | feature envy | major | 11 | with_reason | no | **yes** | no | [12805_org.eclipse.elk.alg.radial.options._cr…](../v04_misleading_feature_envy/12805_org.eclipse.elk.alg.radial.options._create.md) |
| 14835 | feature envy | major | 62 | not_discussed | **yes** | no | **yes** | [14835_org.apache.fop.svg.AbstractFOPImageEle…](../v04_misleading_feature_envy/14835_org.apache.fop.svg.AbstractFOPImageElementBridge_createImageGraphicsNode_BridgeC.md) |
| 15149 | feature envy | major | 51 | with_reason | **yes** | no | no | [15149_org.apache.aries.spifly.statictool.Mai…](../v04_misleading_feature_envy/15149_org.apache.aries.spifly.statictool.Main.weaveDir_File_String_String_String.md) |
| 804 | long method | major | 66 | with_reason | no | no | no | [00804_org.eclipse.orion.server.cf.loggregato…](00804_org.eclipse.orion.server.cf.loggregator.LoggregatorMessage.Message.Builder_merge.md) |
| 1673 | long method | major | 62 | with_reason | no | no | no | [01673_com.facebook.buck.distributed.thrift.F…](01673_com.facebook.buck.distributed.thrift.FetchRuleKeyLogsRequest.FetchRuleKeyLogsReq.md) |
| 3204 | long method | critical | 6 | with_reason | no | **yes** | no | [03204_D.m.md…](03204_D.m.md) |
