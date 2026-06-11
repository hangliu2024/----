# AI Agent Registry - 代理注册中心
# 管理所有AI Agent的注册、发现和调用

class AgentRegistry:
    """AI Agent注册中心，管理所有可用的Agent"""
    
    _agents = {}
    
    @classmethod
    def register(cls, agent_id, name, description, icon, color, route, capabilities):
        """注册一个Agent"""
        cls._agents[agent_id] = {
            'id': agent_id,
            'name': name,
            'description': description,
            'icon': icon,
            'color': color,
            'route': route,
            'capabilities': capabilities,
            'enabled': True
        }
    
    @classmethod
    def get(cls, agent_id):
        """获取指定Agent"""
        return cls._agents.get(agent_id)
    
    @classmethod
    def get_all(cls):
        """获取所有Agent"""
        return cls._agents
    
    @classmethod
    def get_enabled(cls):
        """获取所有启用的Agent"""
        return {k: v for k, v in cls._agents.items() if v.get('enabled', True)}
    
    @classmethod
    def toggle(cls, agent_id, enabled=None):
        """切换Agent启用状态"""
        if agent_id in cls._agents:
            if enabled is not None:
                cls._agents[agent_id]['enabled'] = enabled
            else:
                cls._agents[agent_id]['enabled'] = not cls._agents[agent_id].get('enabled', True)
            return True
        return False


# 注册所有内置Agent
AgentRegistry.register(
    agent_id='audit_assistant',
    name='稽查助手',
    description='智能稽查辅助Agent，自动分析稽查数据、生成稽查建议、辅助稽查记录填写，提升稽查工作效率',
    icon='bi-shield-check',
    color='#ff6700',
    route='ai_agents.audit_agent',
    capabilities=[
        '自动分析稽查任务，生成检查要点',
        '根据稽查类型推荐检查清单',
        '辅助填写稽查记录和整改建议',
        '智能分析稽查历史数据，发现风险趋势',
        '生成稽查报告摘要',
    ]
)

AgentRegistry.register(
    agent_id='form_assistant',
    name='智能填表助手',
    description='自动分析数据并智能填写各类表单，支持人员信息、资产信息、保密管理等表单的自动填充',
    icon='bi-file-earmark-text',
    color='#1890ff',
    route='ai_agents.form_agent',
    capabilities=[
        '根据工号/姓名自动填充人员信息表单',
        '根据使用人自动关联电脑资产信息',
        '智能分析表单数据完整性',
        '批量生成涉密人员/介质登记表',
        '表单数据校验和纠错建议',
    ]
)

AgentRegistry.register(
    agent_id='report_assistant',
    name='报告生成助手',
    description='基于数据自动生成各类分析报告、工作总结、汇报材料，支持多种输出格式',
    icon='bi-graph-up-arrow',
    color='#52c41a',
    route='ai_agents.report_agent',
    capabilities=[
        '生成部门人员统计分析报告',
        '生成资产盘点汇总报告',
        '生成稽查工作总结报告',
        '生成保密检查情况通报',
        '自定义报告模板和格式',
    ]
)

AgentRegistry.register(
    agent_id='risk_analyzer',
    name='风险分析助手',
    description='智能分析信息安全和资产管理中的潜在风险，提供预警和处置建议',
    icon='bi-exclamation-diamond',
    color='#ff4d4f',
    route='ai_agents.risk_agent',
    capabilities=[
        '分析离职人员涉密资产清理情况',
        '检测未分配使用人的涉密电脑',
        '识别权限配置异常和越权风险',
        '分析保密区域管理薄弱环节',
        '生成风险预警和处置建议',
    ]
)